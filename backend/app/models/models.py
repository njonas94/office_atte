from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    WARNING = "warning"

class DataQualityIssueType(str, Enum):
    MISSING_EXIT = "missing_exit"
    MISSING_ENTRY = "missing_entry"
    MULTIPLE_ENTRIES = "multiple_entries"
    INVALID_SEQUENCE = "invalid_sequence"

class EmployeeInfo(BaseModel):
    id_persona: int
    nombre: str
    apellido: str
    departamento: Optional[str]
    email: Optional[str]

class AttendanceRecord(BaseModel):
    id_persona: int
    fecha_fichada: datetime
    prioridad: Optional[int]
    ignorar: Optional[int]

class DailyAttendance(BaseModel):
    date: datetime
    entry_time: Optional[datetime]
    exit_time: Optional[datetime]
    hours_worked: Optional[float]
    is_complete: bool
    meets_9h_requirement: bool

class WeeklyPattern(BaseModel):
    week_start: datetime
    week_end: datetime
    days_attended: int
    total_hours: float
    days_details: List[DailyAttendance]
    meets_pattern_requirement: bool  # 1 or 2 days per week

class MonthlyStats(BaseModel):
    employee_id: int
    year: int
    month: int
    total_days_attended: int
    total_hours_worked: float
    average_hours_per_day: float
    weekly_patterns: List[WeeklyPattern]
    days_compliance: ComplianceStatus
    hours_compliance: ComplianceStatus
    overall_compliance: ComplianceStatus
    weeks_with_1_day: int
    weeks_with_2_days: int
    pattern_compliance: bool

class DataQualityIssue(BaseModel):
    employee_id: int
    employee_name: str
    date: datetime
    issue_type: DataQualityIssueType
    description: str
    total_records: int
    first_record: Optional[datetime]
    last_record: Optional[datetime]

class AttendanceStats(BaseModel):
    employee_info: EmployeeInfo
    monthly_stats: MonthlyStats
    data_quality_issues: List[DataQualityIssue]

class DashboardStats(BaseModel):
    total_employees: int
    compliant_employees: int
    non_compliant_employees: int
    compliance_rate: float
    total_data_issues: int
    average_hours_per_day: float
    most_common_issues: List[Dict[str, Any]]

class MonthlyReport(BaseModel):
    year: int
    month: int
    total_employees: int
    compliance_summary: Dict[str, int]
    employee_stats: List[AttendanceStats]
    data_quality_summary: List[DataQualityIssue]
    department_summary: Dict[str, Dict[str, Any]]

class TrendData(BaseModel):
    month: str
    days_attended: int
    total_hours: float
    compliance_status: ComplianceStatus
    hours_compliance: bool
    pattern_compliance: bool

class EmployeeTrends(BaseModel):
    employee_info: EmployeeInfo
    trend_data: List[TrendData]
    overall_trend: str  # "improving", "declining", "stable"

class DepartmentStats(BaseModel):
    department_name: str
    total_employees: int
    compliant_employees: int
    average_compliance_rate: float
    average_hours_per_employee: float
    total_data_issues: int

class Persona(BaseModel):
    ID_PERSONA: int
    NOMBRE: str
    APELLIDO: str
    NUMERO_DOCUMENTO: str | None