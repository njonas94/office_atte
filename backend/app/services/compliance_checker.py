from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ComplianceChecker:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    async def check_employee_compliance(
        self, 
        employee_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Verifica el cumplimiento de un empleado en un período específico
        """
        try:
            # Asegurar que la conexión esté establecida
            if not self.db_manager.connection:
                await self.db_manager.connect()
            
            # Obtener datos de asistencia del empleado
            attendance_data = await self.db_manager.get_employee_attendance(
                employee_id, start_date, end_date
            )
            
            if not attendance_data:
                return {
                    "employee_id": employee_id,
                    "period": f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}",
                    "compliance": False,
                    "reason": "No hay datos de asistencia en el período",
                    "details": {}
                }
            
            # Analizar cumplimiento
            compliance_result = self._analyze_compliance(attendance_data, start_date, end_date)
            
            return {
                "employee_id": employee_id,
                "period": f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}",
                "compliance": compliance_result["overall_compliance"],
                "reason": compliance_result["reason"],
                "details": compliance_result["details"]
            }
            
        except Exception as e:
            logger.error(f"Error checking compliance for employee {employee_id}: {e}")
            raise
    
    def _analyze_compliance(
        self, 
        attendance_data: List[Dict], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Analiza los datos de asistencia para determinar cumplimiento
        """
        # Agrupar por día
        daily_attendance = self._group_by_day(attendance_data, start_date, end_date)
        
        # Verificar reglas
        rule_1_result = self._check_minimum_days(daily_attendance, len(attendance_data))
        rule_2_result = self._check_weekly_distribution(daily_attendance, start_date, end_date)
        rule_3_result = self._check_minimum_hours(daily_attendance)
        
        # Resultado general
        overall_compliance = all([
            rule_1_result["compliant"],
            rule_2_result["compliant"],
            rule_3_result["compliant"]
        ])
        
        # Determinar razón del incumplimiento
        reason = "Cumple con todas las reglas"
        if not overall_compliance:
            reasons = []
            if not rule_1_result["compliant"]:
                reasons.append(f"Regla 1: {rule_1_result['reason']}")
            if not rule_2_result["compliant"]:
                reasons.append(f"Regla 2: {rule_2_result['reason']}")
            if not rule_3_result["compliant"]:
                reasons.append(f"Regla 3: {rule_3_result['reason']}")
            reason = "; ".join(reasons)
        
        return {
            "overall_compliance": overall_compliance,
            "reason": reason,
            "details": {
                "rule_1_minimum_days": rule_1_result,
                "rule_2_weekly_distribution": rule_2_result,
                "rule_3_minimum_hours": rule_3_result,
                "daily_attendance": daily_attendance
            }
        }
    
    def _group_by_day(self, attendance_data: List[Dict], start_date: datetime = None, end_date: datetime = None) -> Dict[str, List[Dict]]:
        """
        Agrupa los registros de asistencia por día
        """
        from datetime import datetime  # Import al inicio del método
        
        daily_groups = {}
        total_records = len(attendance_data)
        records_in_period = 0
        records_outside_period = 0
        records_processed = 0
        
        logger.info(f"DEBUG: Iniciando _group_by_day con {total_records} registros")
        
        for i, record in enumerate(attendance_data):
            try:
                # Manejar diferentes tipos de fecha
                fecha_fichada = record.get('FECHA_FICHADA')
                logger.debug(f"DEBUG: Procesando registro {i}, fecha: {fecha_fichada}, tipo: {type(fecha_fichada)}")
                
                # Si ya es un objeto datetime (Oracle nativo), usarlo directamente
                if isinstance(fecha_fichada, datetime):
                    logger.debug(f"DEBUG: Fecha ya es datetime: {fecha_fichada}")
                    pass  # Ya es datetime, no hacer nada
                elif isinstance(fecha_fichada, str):
                    # Si es string, convertir a datetime
                    fecha_fichada = datetime.strptime(fecha_fichada, '%Y-%m-%d %H:%M:%S')
                    logger.debug(f"DEBUG: Fecha convertida de string: {fecha_fichada}")
                else:
                    # Si no es datetime válido, saltar este registro
                    logger.warning(f"Fecha inválida en registro: {fecha_fichada} (tipo: {type(fecha_fichada)})")
                    continue
                
                # Contar registros dentro y fuera del período para debugging
                if start_date and end_date:
                    logger.debug(f"DEBUG: Comparando fecha {fecha_fichada} con período {start_date} a {end_date}")
                    if fecha_fichada < start_date or fecha_fichada > end_date:
                        records_outside_period += 1
                        logger.debug(f"DEBUG: Fecha fuera del período: {fecha_fichada}")
                        continue
                    else:
                        records_in_period += 1
                        logger.debug(f"DEBUG: Fecha dentro del período: {fecha_fichada}")
                
                date_key = fecha_fichada.strftime('%Y-%m-%d')
                logger.debug(f"DEBUG: Clave de fecha generada: {date_key}")
                
                if date_key not in daily_groups:
                    daily_groups[date_key] = []
                
                daily_groups[date_key].append(record)
                records_processed += 1
                
            except Exception as e:
                logger.error(f"Error procesando fecha del registro {i}: {e}")
                continue
        
        # Log para debugging
        logger.info(f"DEBUG: Total registros: {total_records}, En período: {records_in_period}, Fuera período: {records_outside_period}, Procesados: {records_processed}")
        logger.info(f"DEBUG: Días encontrados: {len(daily_groups)}, Claves: {list(daily_groups.keys())}")
        
        return daily_groups
    
    def _check_minimum_days(self, daily_attendance: Dict[str, List[Dict]], total_records: int = 0) -> Dict[str, Any]:
        """
        Regla 1: Verificar mínimo 6 días al mes
        """
        days_with_attendance = len(daily_attendance)
        min_required = 6
        
        compliant = days_with_attendance >= min_required
        
        # Crear mensaje más informativo
        if total_records > 0 and days_with_attendance == 0:
            reason = f"Se requieren mínimo {min_required} días, se asistió {days_with_attendance} días (Total registros: {total_records}, pero ninguno en el período especificado)"
        else:
            reason = f"Se requieren mínimo {min_required} días, se asistió {days_with_attendance} días"
        
        return {
            "compliant": compliant,
            "days_attended": days_with_attendance,
            "min_required": min_required,
            "total_records_available": total_records,
            "reason": reason
        }
    
    def _check_weekly_distribution(
        self, 
        daily_attendance: Dict[str, List[Dict]], 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Regla 2: Verificar al menos 1 día por semana
        """
        weeks_with_attendance = set()
        
        for date_str in daily_attendance.keys():
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                # Calcular semana relativa al período en lugar de semana del año
                days_since_start = (date_obj - start_date).days
                week_number = (days_since_start // 7) + 1
                weeks_with_attendance.add(week_number)
            except Exception as e:
                logger.warning(f"Error procesando fecha para distribución semanal: {e}")
                continue
        
        # Calcular semanas en el período
        total_weeks = self._count_weeks_in_period(start_date, end_date)
        min_weeks_required = max(1, total_weeks)  # Al menos 1 semana
        
        compliant = len(weeks_with_attendance) >= min_weeks_required
        
        return {
            "compliant": compliant,
            "weeks_with_attendance": len(weeks_with_attendance),
            "total_weeks_in_period": total_weeks,
            "min_weeks_required": min_weeks_required,
            "reason": f"Se requiere asistencia en al menos {min_weeks_required} semana(s), se asistió en {len(weeks_with_attendance)} semana(s)"
        }
    
    def _check_minimum_hours(self, daily_attendance: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Regla 3: Verificar mínimo 8 horas por día de asistencia
        """
        days_meeting_hours = 0
        total_days = len(daily_attendance)
        
        for day_records in daily_attendance.values():
            if self._day_meets_minimum_hours(day_records):
                days_meeting_hours += 1
        
        min_days_required = 6  # Mínimo 6 días con 8+ horas
        compliant = days_meeting_hours >= min_days_required
        
        return {
            "compliant": compliant,
            "days_meeting_hours": days_meeting_hours,
            "total_days": total_days,
            "min_days_required": min_days_required,
            "reason": f"Se requieren mínimo {min_days_required} días con 8+ horas, se cumplió en {days_meeting_hours} días"
        }
    
    def _day_meets_minimum_hours(self, day_records: List[Dict]) -> bool:
        """
        Verifica si un día cumple con el mínimo de 8 horas
        """
        if len(day_records) < 2:  # Necesitamos entrada y salida
            return False
        
        try:
            # Ordenar registros por hora
            sorted_records = sorted(day_records, key=lambda x: x.get('FECHA_FICHADA', ''))
            
            # Calcular horas trabajadas
            total_hours = 0
            
            for i in range(0, len(sorted_records) - 1, 2):
                if i + 1 < len(sorted_records):
                    entry_time = sorted_records[i].get('FECHA_FICHADA')
                    exit_time = sorted_records[i + 1].get('FECHA_FICHADA')
                    
                    # Manejar diferentes tipos de fecha
                    if isinstance(entry_time, str):
                        entry_time = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
                    elif not isinstance(entry_time, datetime):
                        logger.warning(f"Tipo de fecha de entrada inválido: {type(entry_time)}")
                        continue
                        
                    if isinstance(exit_time, str):
                        exit_time = datetime.strptime(exit_time, '%Y-%m-%d %H:%M:%S')
                    elif not isinstance(exit_time, datetime):
                        logger.warning(f"Tipo de fecha de salida inválido: {type(exit_time)}")
                        continue
                    
                    time_diff = exit_time - entry_time
                    total_hours += time_diff.total_seconds() / 3600  # Convertir a horas
            
            return total_hours >= 8.0
            
        except Exception as e:
            logger.error(f"Error calculando horas del día: {e}")
            return False
    
    def _count_weeks_in_period(self, start_date: datetime, end_date: datetime) -> int:
        """
        Cuenta el número de semanas en un período
        """
        try:
            # Calcular semanas reales en el período
            days_diff = (end_date - start_date).days
            weeks_count = max(1, (days_diff // 7) + 1)
            
            # Verificar que no exceda el máximo lógico (5 semanas máximo para un mes)
            if weeks_count > 5:
                weeks_count = 5
                
            return weeks_count
        except Exception as e:
            logger.error(f"Error contando semanas: {e}")
            # Fallback: calcular semanas aproximadas
            days_diff = (end_date - start_date).days
            return max(1, min(5, (days_diff // 7) + 1))
    
    async def check_multiple_employees_compliance(
        self, 
        employee_ids: List[int], 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Verifica el cumplimiento de múltiples empleados
        """
        try:
            # Asegurar que la conexión esté establecida
            if not self.db_manager.connection:
                await self.db_manager.connect()
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
        
        results = []
        
        for employee_id in employee_ids:
            try:
                compliance = await self.check_employee_compliance(
                    employee_id, start_date, end_date
                )
                results.append(compliance)
            except Exception as e:
                logger.error(f"Error checking compliance for employee {employee_id}: {e}")
                results.append({
                    "employee_id": employee_id,
                    "period": f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}",
                    "compliance": False,
                    "reason": f"Error al verificar cumplimiento: {str(e)}",
                    "details": {}
                })
        
        return results
