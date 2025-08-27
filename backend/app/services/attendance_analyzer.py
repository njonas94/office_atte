from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import calendar
import logging
from models import (
    ComplianceStatus, DataQualityIssue, DataQualityIssueType,
    DailyAttendance, WeeklyPattern, MonthlyStats, DashboardStats,
    EmployeeTrends, TrendData, DepartmentStats
)

logger = logging.getLogger(__name__)

class AttendanceAnalyzer:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def _parse_daily_attendance(self, records: List[Dict]) -> Dict[str, DailyAttendance]:
        """Parse attendance records into daily attendance objects"""
        daily_records = defaultdict(list)
        
        # Group records by date
        for record in records:
            date_key = record['FECHA_FICHADA'].date()
            daily_records[date_key].append(record)
        
        daily_attendance = {}
        
        for date, day_records in daily_records.items():
            # Sort by time to identify entry and exit
            day_records.sort(key=lambda x: x['FECHA_FICHADA'])
            
            entry_time = None
            exit_time = None
            is_complete = False
            hours_worked = 0.0
            
            if len(day_records) == 2:
                entry_time = day_records[0]['FECHA_FICHADA']
                exit_time = day_records[1]['FECHA_FICHADA']
                is_complete = True
                
                # Calculate hours worked
                time_diff = exit_time - entry_time
                hours_worked = time_diff.total_seconds() / 3600.0
                
            elif len(day_records) == 1:
                # Missing entry or exit
                entry_time = day_records[0]['FECHA_FICHADA']
                is_complete = False
            
            meets_9h_requirement = hours_worked >= 9.0 if is_complete else False
            
            daily_attendance[date] = DailyAttendance(
                date=datetime.combine(date, datetime.min.time()),
                entry_time=entry_time,
                exit_time=exit_time,
                hours_worked=hours_worked if is_complete else None,
                is_complete=is_complete,
                meets_9h_requirement=meets_9h_requirement
            )
        
        return daily_attendance
    
    def _analyze_weekly_patterns(
        self, 
        daily_attendance: Dict[str, DailyAttendance], 
        year: int, 
        month: int
    ) -> List[WeeklyPattern]:
        """Analyze weekly attendance patterns for the month"""
        
        # Get all weeks in the month
        cal = calendar.monthcalendar(year, month)
        weekly_patterns = []
        
        for week in cal:
            # Skip weeks that are mostly from other months
            days_in_current_month = [day for day in week if day != 0]
            if not days_in_current_month:
                continue
            
            week_start = datetime(year, month, days_in_current_month[0])
            week_end = datetime(year, month, days_in_current_month[-1])
            
            # Get attendance for this week
            week_days = []
            days_attended = 0
            total_hours = 0.0
            
            for day in days_in_current_month:
                date_key = datetime(year, month, day).date()
                if date_key in daily_attendance:
                    attendance = daily_attendance[date_key]
                    week_days.append(attendance)
                    if attendance.is_complete:
                        days_attended += 1
                        total_hours += attendance.hours_worked or 0
            
            # Check if pattern meets requirements (1 or 2 days per week)
            meets_pattern_requirement = days_attended in [1, 2]
            
            weekly_patterns.append(WeeklyPattern(
                week_start=week_start,
                week_end=week_end,
                days_attended=days_attended,
                total_hours=total_hours,
                days_details=week_days,
                meets_pattern_requirement=meets_pattern_requirement
            ))
        
        return weekly_patterns
    
    def _evaluate_compliance(
        self, 
        weekly_patterns: List[WeeklyPattern], 
        total_days_attended: int,
        total_hours_worked: float
    ) -> Tuple[ComplianceStatus, ComplianceStatus, ComplianceStatus, bool]:
        """Evaluate compliance based on attendance patterns"""
        
        # Days compliance: minimum 6 days per month
        if total_days_attended >= 6:
            days_compliance = ComplianceStatus.COMPLIANT
        elif total_days_attended >= 4:
            days_compliance = ComplianceStatus.PARTIAL
        else:
            days_compliance = ComplianceStatus.NON_COMPLIANT
        
        # Hours compliance: minimum 9 hours per attended day
        valid_days = sum(1 for pattern in weekly_patterns for day in pattern.days_details if day.is_complete)
        hours_compliant_days = sum(1 for pattern in weekly_patterns for day in pattern.days_details 
                                 if day.is_complete and day.meets_9h_requirement)
        
        if valid_days == 0:
            hours_compliance = ComplianceStatus.NON_COMPLIANT
        elif hours_compliant_days == valid_days:
            hours_compliance = ComplianceStatus.COMPLIANT
        elif hours_compliant_days >= valid_days * 0.8:
            hours_compliance = ComplianceStatus.PARTIAL
        else:
            hours_compliance = ComplianceStatus.NON_COMPLIANT
        
        # Pattern compliance: flexible distribution but respecting week limits
        weeks_with_1_day = sum(1 for pattern in weekly_patterns if pattern.days_attended == 1)
        weeks_with_2_days = sum(1 for pattern in weekly_patterns if pattern.days_attended == 2)
        weeks_with_invalid = sum(1 for pattern in weekly_patterns if pattern.days_attended > 2)
        
        pattern_compliance = weeks_with_invalid == 0
        
        # Overall compliance
        if (days_compliance == ComplianceStatus.COMPLIANT and 
            hours_compliance == ComplianceStatus.COMPLIANT and 
            pattern_compliance):
            overall_compliance = ComplianceStatus.COMPLIANT
        elif days_compliance == ComplianceStatus.NON_COMPLIANT or hours_compliance == ComplianceStatus.NON_COMPLIANT:
            overall_compliance = ComplianceStatus.NON_COMPLIANT
        else:
            overall_compliance = ComplianceStatus.PARTIAL
        
        return days_compliance, hours_compliance, overall_compliance, pattern_compliance
    
    async def analyze_employee_month(
        self, 
        employee_id: int, 
        year: int, 
        month: int
    ) -> MonthlyStats:
        """Analyze attendance for a specific employee and month"""
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Get attendance records
        records = await self.db_manager.get_employee_attendance(
            employee_id, start_date, end_date
        )
        
        # Parse daily attendance
        daily_attendance = self._parse_daily_attendance(records)
        
        # Analyze weekly patterns
        weekly_patterns = self._analyze_weekly_patterns(daily_attendance, year, month)
        
        # Calculate totals
        total_days_attended = sum(pattern.days_attended for pattern in weekly_patterns)
        total_hours_worked = sum(pattern.total_hours for pattern in weekly_patterns)
        average_hours_per_day = total_hours_worked / total_days_attended if total_days_attended > 0 else 0
        
        # Evaluate compliance
        days_compliance, hours_compliance, overall_compliance, pattern_compliance = self._evaluate_compliance(
            weekly_patterns, total_days_attended, total_hours_worked
        )
        
        # Count week patterns
        weeks_with_1_day = sum(1 for pattern in weekly_patterns if pattern.days_attended == 1)
        weeks_with_2_days = sum(1 for pattern in weekly_patterns if pattern.days_attended == 2)
        
        return MonthlyStats(
            employee_id=employee_id,
            year=year,
            month=month,
            total_days_attended=total_days_attended,
            total_hours_worked=total_hours_worked,
            average_hours_per_day=average_hours_per_day,
            weekly_patterns=weekly_patterns,
            days_compliance=days_compliance,
            hours_compliance=hours_compliance,
            overall_compliance=overall_compliance,
            weeks_with_1_day=weeks_with_1_day,
            weeks_with_2_days=weeks_with_2_days,
            pattern_compliance=pattern_compliance
        )
    
    async def generate_monthly_compliance_report(
        self, 
        year: int, 
        month: int
    ) -> Dict[str, Any]:
        """Generate monthly compliance report for all employees"""
        
        employees = await self.db_manager.get_all_employees()
        employee_stats = []
        
        compliance_summary = {
            'compliant': 0,
            'partial': 0,
            'non_compliant': 0,
            'warning': 0
        }
        
        for employee in employees:
            try:
                stats = await self.analyze_employee_month(
                    employee['ID_PERSONA'], year, month
                )
                
                employee_stats.append({
                    'employee_info': employee,
                    'stats': stats
                })
                
                compliance_summary[stats.overall_compliance.value] += 1
                
            except Exception as e:
                logger.error(f"Error analyzing employee {employee['ID_PERSONA']}: {e}")
                compliance_summary['warning'] += 1
        
        return {
            'year': year,
            'month': month,
            'total_employees': len(employees),
            'compliance_summary': compliance_summary,
            'employee_stats': employee_stats
        }
    
    async def detect_data_quality_issues(
        self, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[DataQualityIssue]:
        """Detect data quality issues"""
        
        issues_data = await self.db_manager.get_data_quality_issues(start_date, end_date)
        quality_issues = []
        
        for issue in issues_data:
            employee_info = await self.db_manager.get_employee_info(issue['ID_PERSONA'])
            employee_name = f"{employee_info['NOMBRE']} {employee_info['APELLIDO']}" if employee_info else "Unknown"
            
            # Determine issue type
            total_records = issue['TOTAL_REGISTROS']
            if total_records == 1:
                issue_type = DataQualityIssueType.MISSING_EXIT
                description = "Missing exit record - only entry found"
            elif total_records > 2:
                issue_type = DataQualityIssueType.MULTIPLE_ENTRIES
                description = f"Multiple entries found ({total_records} records)"
            else:
                issue_type = DataQualityIssueType.INVALID_SEQUENCE
                description = "Invalid attendance sequence"
            
            quality_issues.append(DataQualityIssue(
                employee_id=issue['ID_PERSONA'],
                employee_name=employee_name,
                date=issue['DIA'],
                issue_type=issue_type,
                description=description,
                total_records=total_records,
                first_record=issue['PRIMER_REGISTRO'],
                last_record=issue['ULTIMO_REGISTRO']
            ))
        
        return quality_issues
    
    async def get_dashboard_statistics(
        self, 
        year: int, 
        month: int
    ) -> DashboardStats:
        """Get general dashboard statistics"""
        
        report = await self.generate_monthly_compliance_report(year, month)
        data_issues = await self.detect_data_quality_issues()
        
        total_employees = report['total_employees']
        compliance_summary = report['compliance_summary']
        
        # Calculate compliance rate
        compliant_employees = compliance_summary['compliant']
        compliance_rate = (compliant_employees / total_employees) * 100 if total_employees > 0 else 0
        
        # Calculate average hours per day
        total_hours = sum(stat['stats'].total_hours_worked for stat in report['employee_stats'])
        total_days = sum(stat['stats'].total_days_attended for stat in report['employee_stats'])
        average_hours_per_day = total_hours / total_days if total_days > 0 else 0
        
        # Most common issues
        issue_counts = defaultdict(int)
        for issue in data_issues:
            issue_counts[issue.issue_type.value] += 1
        
        most_common_issues = [
            {'type': issue_type, 'count': count}
            for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return DashboardStats(
            total_employees=total_employees,
            compliant_employees=compliant_employees,
            non_compliant_employees=compliance_summary['non_compliant'],
            compliance_rate=compliance_rate,
            total_data_issues=len(data_issues),
            average_hours_per_day=average_hours_per_day,
            most_common_issues=most_common_issues
        )
    
    async def get_employee_trends(
        self, 
        employee_id: int, 
        months_back: int = 6
    ) -> EmployeeTrends:
        """Get attendance trends for an employee over multiple months"""
        
        employee_info = await self.db_manager.get_employee_info(employee_id)
        trend_data = []
        
        current_date = datetime.now()
        
        for i in range(months_back):
            # Calculate year and month
            target_date = current_date - timedelta(days=30 * i)
            year = target_date.year
            month = target_date.month
            
            try:
                stats = await self.analyze_employee_month(employee_id, year, month)
                
                trend_data.append(TrendData(
                    month=f"{year}-{month:02d}",
                    days_attended=stats.total_days_attended,
                    total_hours=stats.total_hours_worked,
                    compliance_status=stats.overall_compliance,
                    hours_compliance=stats.hours_compliance == ComplianceStatus.COMPLIANT,
                    pattern_compliance=stats.pattern_compliance
                ))
            except Exception as e:
                logger.error(f"Error getting trends for employee {employee_id}, {year}-{month}: {e}")
        
        # Determine overall trend
        if len(trend_data) >= 3:
            recent_compliance = sum(1 for t in trend_data[:3] if t.compliance_status == ComplianceStatus.COMPLIANT)
            older_compliance = sum(1 for t in trend_data[3:] if t.compliance_status == ComplianceStatus.COMPLIANT)
            
            if recent_compliance > older_compliance:
                overall_trend = "improving"
            elif recent_compliance < older_compliance:
                overall_trend = "declining"
            else:
                overall_trend = "stable"
        else:
            overall_trend = "stable"
        
        return EmployeeTrends(
            employee_info=employee_info,
            trend_data=list(reversed(trend_data)),  # Reverse to show chronological order
            overall_trend=overall_trend
        )
    
    async def get_department_statistics(
        self, 
        year: int, 
        month: int
    ) -> List[DepartmentStats]:
        """Get department-wise attendance statistics"""
        
        employees = await self.db_manager.get_all_employees()
        department_stats = defaultdict(lambda: {
            'total_employees': 0,
            'compliant_employees': 0,
            'total_hours': 0,
            'total_days': 0,
            'data_issues': 0
        })
        
        data_issues = await self.detect_data_quality_issues()
        issue_by_employee = defaultdict(int)
        for issue in data_issues:
            issue_by_employee[issue.employee_id] += 1
        
        for employee in employees:
            dept = employee.get('DEPARTAMENTO', 'Unknown')
            employee_id = employee['ID_PERSONA']
            
            try:
                stats = await self.analyze_employee_month(employee_id, year, month)
                
                department_stats[dept]['total_employees'] += 1
                department_stats[dept]['total_hours'] += stats.total_hours_worked
                department_stats[dept]['total_days'] += stats.total_days_attended
                department_stats[dept]['data_issues'] += issue_by_employee[employee_id]
                
                if stats.overall_compliance == ComplianceStatus.COMPLIANT:
                    department_stats[dept]['compliant_employees'] += 1
                    
            except Exception as e:
                logger.error(f"Error analyzing employee {employee_id} for department stats: {e}")
                department_stats[dept]['total_employees'] += 1
        
        result = []
        for dept_name, stats in department_stats.items():
            compliance_rate = (stats['compliant_employees'] / stats['total_employees']) * 100 if stats['total_employees'] > 0 else 0
            avg_hours = stats['total_hours'] / stats['total_employees'] if stats['total_employees'] > 0 else 0
            
            result.append(DepartmentStats(
                department_name=dept_name,
                total_employees=stats['total_employees'],
                compliant_employees=stats['compliant_employees'],
                average_compliance_rate=compliance_rate,
                average_hours_per_employee=avg_hours,
                total_data_issues=stats['data_issues']
            ))
        
        return sorted(result, key=lambda x: x.average_compliance_rate, reverse=True)
    
    async def analyze_weekly_patterns(
        self, 
        employee_id: int, 
        year: int, 
        month: int
    ) -> Dict[str, Any]:
        """Get detailed weekly patterns analysis for an employee"""
        
        stats = await self.analyze_employee_month(employee_id, year, month)
        employee_info = await self.db_manager.get_employee_info(employee_id)
        
        return {
            'employee_info': employee_info,
            'weekly_patterns': [
                {
                    'week_number': i + 1,
                    'week_start': pattern.week_start.strftime('%Y-%m-%d'),
                    'week_end': pattern.week_end.strftime('%Y-%m-%d'),
                    'days_attended': pattern.days_attended,
                    'total_hours': round(pattern.total_hours, 2),
                    'meets_requirement': pattern.meets_pattern_requirement,
                    'daily_details': [
                        {
                            'date': day.date.strftime('%Y-%m-%d'),
                            'entry_time': day.entry_time.strftime('%H:%M') if day.entry_time else None,
                            'exit_time': day.exit_time.strftime('%H:%M') if day.exit_time else None,
                            'hours_worked': round(day.hours_worked, 2) if day.hours_worked else None,
                            'is_complete': day.is_complete,
                            'meets_9h': day.meets_9h_requirement
                        }
                        for day in pattern.days_details
                    ]
                }
                for i, pattern in enumerate(stats.weekly_patterns)
            ],
            'summary': {
                'total_days': stats.total_days_attended,
                'total_hours': round(stats.total_hours_worked, 2),
                'average_hours_per_day': round(stats.average_hours_per_day, 2),
                'weeks_with_1_day': stats.weeks_with_1_day,
                'weeks_with_2_days': stats.weeks_with_2_days,
                'days_compliance': stats.days_compliance.value,
                'hours_compliance': stats.hours_compliance.value,
                'pattern_compliance': stats.pattern_compliance,
                'overall_compliance': stats.overall_compliance.value
            }
        }