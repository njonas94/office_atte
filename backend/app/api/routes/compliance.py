from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional
from app.services.compliance_checker import ComplianceChecker
from app.db.database_manager import DatabaseManager

router = APIRouter()
db_manager = DatabaseManager()
compliance_checker = ComplianceChecker(db_manager)

@router.get("/compliance/employee/{employee_id}")
async def check_employee_compliance(
    employee_id: int,
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    months: Optional[int] = Query(1, description="Número de meses hacia atrás (1, 3, 6, 12)")
):
    """
    Verifica el cumplimiento de un empleado específico
    """
    try:
        # Calcular fechas si no se proporcionan
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30 * months)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Verificar cumplimiento
        compliance = await compliance_checker.check_employee_compliance(
            employee_id, start_date, end_date
        )
        
        return compliance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance/multiple-employees")
async def check_multiple_employees_compliance(
    employee_ids: List[int],
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    months: Optional[int] = Query(1, description="Número de meses hacia atrás (1, 3, 6, 12)")
):
    """
    Verifica el cumplimiento de múltiples empleados
    """
    try:
        # Calcular fechas si no se proporcionan
        if not start_date or not end_date:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30 * months)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Verificar cumplimiento de múltiples empleados
        compliance_results = await compliance_checker.check_multiple_employees_compliance(
            employee_ids, start_date, end_date
        )
        
        return {
            "period": f"{start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}",
            "total_employees": len(employee_ids),
            "compliant_employees": sum(1 for r in compliance_results if r["compliance"]),
            "non_compliant_employees": sum(1 for r in compliance_results if not r["compliance"]),
            "results": compliance_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance/periods")
async def get_compliance_periods():
    """
    Obtiene los períodos predefinidos disponibles para consulta
    """
    return {
        "available_periods": [
            {
                "name": "Último mes",
                "months": 1,
                "description": "Verificar cumplimiento del último mes calendario"
            },
            {
                "name": "Últimos 3 meses",
                "months": 3,
                "description": "Verificar cumplimiento de los últimos 3 meses"
            },
            {
                "name": "Últimos 6 meses",
                "months": 6,
                "description": "Verificar cumplimiento de los últimos 6 meses"
            },
            {
                "name": "Último año",
                "months": 12,
                "description": "Verificar cumplimiento del último año"
            }
        ]
    }

@router.get("/compliance/rules")
async def get_compliance_rules():
    """
    Obtiene las reglas de cumplimiento de asistencia
    """
    return {
        "rules": [
            {
                "rule_id": 1,
                "name": "Mínimo de días",
                "description": "Cumplir con un mínimo de 6 días al mes en la oficina",
                "requirement": "6 días mínimo por mes"
            },
            {
                "rule_id": 2,
                "name": "Distribución semanal",
                "description": "Ninguna semana debe quedar sin al menos 1 día de asistencia",
                "requirement": "Al menos 1 día por semana"
            },
            {
                "rule_id": 3,
                "name": "Horas mínimas",
                "description": "Cumplir con 8 horas en la oficina en los días de asistencia",
                "requirement": "8 horas mínimas por día de asistencia"
            }
        ],
        "example": {
            "description": "Ejemplo de distribución válida: 2 días en las primeras dos semanas (8+ horas) y 1 día en las dos últimas semanas (8+ horas)",
            "note": "Se cuentan los días calendario"
        }
    }

@router.get("/compliance/test-attendance/{employee_id}")
async def test_attendance_query(employee_id: int):
    """
    Endpoint de prueba para diagnosticar problemas con la consulta de asistencia
    """
    try:
        from datetime import datetime, timedelta
        from app.db.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        if not db_manager.connection:
            await db_manager.connect()
        
        # Fechas de prueba
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Probar consulta simple
        query = """
        SELECT COUNT(*) as total_records
        FROM CRONOS.FICHADA_PROCESO 
        WHERE ID_PERSONA = :employee_id 
        AND TRUNC(FECHA_FICHADA) >= TRUNC(:start_date)
        AND TRUNC(FECHA_FICHADA) <= TRUNC(:end_date)
        """
        
        cursor = db_manager.connection.cursor()
        cursor.execute(query, {
            'employee_id': employee_id,
            'start_date': start_date,
            'end_date': end_date
        })
        
        result = cursor.fetchone()
        cursor.close()
        
        return {
            "employee_id": employee_id,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "total_records": result[0] if result else 0,
            "query_executed": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id
        }

@router.get("/compliance/test-logic/{employee_id}")
async def test_compliance_logic(employee_id: int):
    """
    Endpoint de prueba para diagnosticar problemas con la lógica del ComplianceChecker
    """
    try:
        from datetime import datetime, timedelta
        from app.services.compliance_checker import ComplianceChecker
        from app.db.database_manager import DatabaseManager
        
        # Crear instancias
        db_manager = DatabaseManager()
        compliance_checker = ComplianceChecker(db_manager)
        
        # Conectar a la base de datos
        if not db_manager.connection:
            await db_manager.connect()
        
        # Fechas de prueba
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Obtener datos de asistencia
        attendance_data = await db_manager.get_employee_attendance(
            employee_id, start_date, end_date
        )
        
        # Probar solo la lógica de agrupación por día
        daily_attendance = compliance_checker._group_by_day(attendance_data)
        
        return {
            "employee_id": employee_id,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "total_records": len(attendance_data),
            "daily_groups": len(daily_attendance),
            "daily_keys": list(daily_attendance.keys()),
            "logic_test": "successful"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id,
            "traceback": str(e.__traceback__) if hasattr(e, '__traceback__') else "No traceback"
        }

@router.get("/compliance/test-group-by-day/{employee_id}")
async def test_group_by_day(employee_id: int):
    """
    Endpoint de prueba específico para el método _group_by_day
    """
    try:
        from datetime import datetime, timedelta
        from app.db.database_manager import DatabaseManager
        
        # Conectar a la base de datos
        db_manager = DatabaseManager()
        if not db_manager.connection:
            await db_manager.connect()
        
        # Fechas de prueba
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Obtener datos de asistencia
        attendance_data = await db_manager.get_employee_attendance(
            employee_id, start_date, end_date
        )
        
        # Probar el método _group_by_day paso a paso
        daily_groups = {}
        
        for i, record in enumerate(attendance_data):
            try:
                # Mostrar información del registro
                record_info = {
                    "index": i,
                    "record_keys": list(record.keys()),
                    "fecha_fichada_type": type(record.get('FECHA_FICHADA')).__name__,
                    "fecha_fichada_value": str(record.get('FECHA_FICHADA')),
                    "id_persona_type": type(record.get('ID_PERSONA')).__name__,
                    "id_persona_value": str(record.get('ID_PERSONA'))
                }
                
                # Procesar fecha
                fecha_fichada = record.get('FECHA_FICHADA')
                if isinstance(fecha_fichada, str):
                    fecha_fichada = datetime.strptime(fecha_fichada, '%Y-%m-%d %H:%M:%S')
                elif not isinstance(fecha_fichada, datetime):
                    record_info["error"] = f"Tipo de fecha inválido: {type(fecha_fichada)}"
                    continue
                
                date_key = fecha_fichada.strftime('%Y-%m-%d')
                
                if date_key not in daily_groups:
                    daily_groups[date_key] = []
                
                daily_groups[date_key].append(record)
                record_info["processed"] = True
                record_info["date_key"] = date_key
                
            except Exception as e:
                record_info = {
                    "index": i,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            
            # Solo procesar los primeros 3 registros para diagnóstico
            if i >= 2:
                break
        
        return {
            "employee_id": employee_id,
            "total_records": len(attendance_data),
            "processed_records": min(3, len(attendance_data)),
            "daily_groups_count": len(daily_groups),
            "daily_groups_keys": list(daily_groups.keys()),
            "record_analysis": record_info
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id
        }

@router.get("/compliance/debug-sql/{employee_id}")
async def debug_sql_query(employee_id: int):
    """
    Endpoint para debuggear la consulta SQL directamente
    """
    try:
        from datetime import datetime, timedelta
        import cx_Oracle
        
        # Conectar directamente a la base de datos
        from app.db.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        if not db_manager.connection:
            await db_manager.connect()
        
        # Fechas de prueba
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Consulta SQL directa para debug
        query = """
        SELECT ID_PERSONA, FECHA_FICHADA, 
               PRIORIDAD,
               IGNORAR
        FROM CRONOS.FICHADA_PROCESO 
        WHERE ID_PERSONA = :employee_id 
        AND ROWNUM <= 100
        AND (IGNORAR = 0 OR IGNORAR IS NULL)
        ORDER BY FECHA_FICHADA
        """
        
        try:
            cursor = db_manager.connection.cursor()
            
            # Mostrar los tipos de datos que vamos a pasar
            debug_info = {
                "employee_id_type": type(employee_id).__name__,
                "employee_id_value": employee_id,
                "start_date_type": type(start_date).__name__,
                "start_date_value": start_date.strftime('%Y-%m-%d'),
                "end_date_type": type(end_date).__name__,
                "end_date_value": end_date.strftime('%Y-%m-%d')
            }
            
            # Ejecutar la consulta
            cursor.execute(query, {
                'employee_id': str(employee_id)
            })
            
            columns = [col[0] for col in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            
            return {
                "success": True,
                "employee_id": employee_id,
                "total_records": len(records),
                "debug_info": debug_info,
                "first_record": records[0] if records else None,
                "columns": columns
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "debug_info": debug_info,
                "query": query
            }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id
        }

@router.get("/compliance/test-minimal/{employee_id}")
async def test_minimal_query(employee_id: int):
    """
    Endpoint de prueba con consulta SQL mínima para identificar el problema
    """
    try:
        from app.db.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        if not db_manager.connection:
            await db_manager.connect()
        
        # Probar consultas SQL paso a paso
        tests = []
        
        # Test 1: Consulta básica sin WHERE
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM CRONOS.FICHADA_PROCESO")
            count = cursor.fetchone()[0]
            cursor.close()
            tests.append({"test": "count_all", "success": True, "result": count})
        except Exception as e:
            tests.append({"test": "count_all", "success": False, "error": str(e)})
        
        # Test 2: Consulta con ID_PERSONA simple
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT ID_PERSONA FROM CRONOS.FICHADA_PROCESO WHERE ROWNUM <= 5")
            records = cursor.fetchall()
            cursor.close()
            tests.append({"test": "simple_id_query", "success": True, "result": [str(r[0]) for r in records]})
        except Exception as e:
            tests.append({"test": "simple_id_query", "success": False, "error": str(e)})
        
        # Test 3: Consulta con fecha simple
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute("SELECT FECHA_FICHADA FROM CRONOS.FICHADA_PROCESO WHERE ROWNUM <= 3")
            records = cursor.fetchall()
            cursor.close()
            tests.append({"test": "simple_date_query", "success": True, "result": [str(r[0]) for r in records]})
        except Exception as e:
            tests.append({"test": "simple_date_query", "success": False, "error": str(e)})
        
        return {
            "employee_id": employee_id,
            "tests": tests
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id
        }

@router.get("/compliance/test-working-query/{employee_id}")
async def test_working_query(employee_id: int):
    """
    Endpoint de prueba usando la misma consulta que funciona en el endpoint simple
    """
    try:
        from app.db.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        if not db_manager.connection:
            await db_manager.connect()
        
        # Usar la misma consulta que funciona en el endpoint simple
        query = """
        SELECT ID_PERSONA, FECHA_FICHADA, 
               CASE WHEN PRIORIDAD IS NULL THEN 0 ELSE PRIORIDAD END as PRIORIDAD,
               CASE WHEN IGNORAR IS NULL THEN 0 ELSE IGNORAR END as IGNORAR
        FROM CRONOS.FICHADA_PROCESO 
        WHERE ID_PERSONA = :employee_id 
        AND ROWNUM <= 10
        """
        
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute(query, {'employee_id': str(employee_id)})
            
            columns = [col[0] for col in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            
            return {
                "success": True,
                "employee_id": employee_id,
                "total_records": len(records),
                "first_record": records[0] if records else None,
                "columns": columns
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "query": query
            }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id
        }

@router.get("/compliance/test-basic-fields/{employee_id}")
async def test_basic_fields(employee_id: int):
    """
    Endpoint de prueba usando solo campos básicos sin funciones CASE
    """
    try:
        from app.db.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        if not db_manager.connection:
            await db_manager.connect()
        
        # Consulta SQL básica sin funciones CASE
        query = """
        SELECT ID_PERSONA, FECHA_FICHADA
        FROM CRONOS.FICHADA_PROCESO 
        WHERE ID_PERSONA = :employee_id 
        AND ROWNUM <= 5
        """
        
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute(query, {'employee_id': str(employee_id)})
            
            columns = [col[0] for col in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            
            return {
                "success": True,
                "employee_id": employee_id,
                "total_records": len(records),
                "first_record": records[0] if records else None,
                "columns": columns
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "query": query
            }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id
        }

@router.get("/compliance/test-final-query/{employee_id}")
async def test_final_query(employee_id: int):
    """
    Endpoint de prueba final usando la consulta que debería funcionar
    """
    try:
        from datetime import datetime, timedelta
        from app.db.database_manager import DatabaseManager
        db_manager = DatabaseManager()
        if not db_manager.connection:
            await db_manager.connect()
        
        # Fechas de prueba
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Consulta SQL final que debería funcionar - usando la misma que funciona
        query = """
        SELECT ID_PERSONA, FECHA_FICHADA
        FROM CRONOS.FICHADA_PROCESO 
        WHERE ID_PERSONA = :employee_id 
        AND ROWNUM <= 100
        ORDER BY FECHA_FICHADA
        """
        
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute(query, {
                'employee_id': str(employee_id)
            })
            
            columns = [col[0] for col in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            
            return {
                "success": True,
                "employee_id": employee_id,
                "total_records": len(records),
                "first_record": records[0] if records else None,
                "columns": columns,
                "start_date": start_date.strftime('%d-%b-%Y').upper(),
                "end_date": end_date.strftime('%d-%b-%Y').upper()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "query": query,
                "start_date": start_date.strftime('%d-%b-%Y').upper(),
                "end_date": end_date.strftime('%d-%b-%Y').upper()
            }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id
        }

@router.get("/compliance/search-august-2025/{employee_id}")
async def search_august_2025(employee_id: int):
    """
    Endpoint específico para buscar registros de agosto de 2025
    """
    try:
        from app.db.database_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        if not db_manager.connection:
            await db_manager.connect()
        
        # Buscar específicamente en agosto de 2025
        query = """
        SELECT ID_PERSONA, FECHA_FICHADA
        FROM CRONOS.FICHADA_PROCESO 
        WHERE ID_PERSONA = :employee_id 
        AND EXTRACT(YEAR FROM FECHA_FICHADA) = 2025
        AND EXTRACT(MONTH FROM FECHA_FICHADA) = 8
        ORDER BY FECHA_FICHADA DESC
        """
        
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute(query, {
                'employee_id': str(employee_id)
            })
            
            columns = [col[0] for col in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            
            # Analizar fechas encontradas
            date_analysis = []
            for i, record in enumerate(records):
                fecha_fichada = record.get('FECHA_FICHADA')
                
                if isinstance(fecha_fichada, str):
                    try:
                        parsed_date = datetime.strptime(fecha_fichada, '%Y-%m-%d %H:%M:%S')
                        date_analysis.append({
                            "index": i,
                            "original_date": fecha_fichada,
                            "parsed_date": parsed_date.strftime('%Y-%m-%d %H:%M:%S'),
                            "day": parsed_date.day,
                            "hour": parsed_date.hour,
                            "minute": parsed_date.minute
                        })
                    except Exception as e:
                        date_analysis.append({
                            "index": i,
                            "original_date": fecha_fichada,
                            "error": str(e)
                        })
                else:
                    date_analysis.append({
                        "index": i,
                        "original_date": str(fecha_fichada),
                        "type": type(fecha_fichada).__name__
                    })
            
            return {
                "success": True,
                "employee_id": employee_id,
                "year_search": 2025,
                "month_search": 8,
                "total_records_august_2025": len(records),
                "date_analysis": date_analysis,
                "query_used": query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "query": query
            }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id
        }

@router.get("/compliance/debug-step-by-step/{employee_id}")
async def debug_step_by_step(employee_id: int):
    """
    Endpoint de debug paso a paso para analizar el proceso de cumplimiento
    """
    try:
        from datetime import datetime, timedelta
        from app.db.database_manager import DatabaseManager
        from app.services.compliance_checker import ComplianceChecker
        
        db_manager = DatabaseManager()
        if not db_manager.connection:
            await db_manager.connect()
        
        # Fechas de prueba
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Paso 1: Obtener datos de asistencia
        attendance_data = await db_manager.get_employee_attendance(
            employee_id, start_date, end_date
        )
        
        # Paso 2: Analizar los datos obtenidos
        data_analysis = {
            "total_records": len(attendance_data),
            "first_5_records": [],
            "date_types": [],
            "date_range_check": []
        }
        
        for i, record in enumerate(attendance_data[:5]):
            fecha_fichada = record.get('FECHA_FICHADA')
            
            if isinstance(fecha_fichada, str):
                try:
                    parsed_date = datetime.strptime(fecha_fichada, '%Y-%m-%d %H:%M:%S')
                    is_in_period = start_date <= parsed_date <= end_date
                    data_analysis["first_5_records"].append({
                        "index": i,
                        "original": fecha_fichada,
                        "parsed": parsed_date.strftime('%Y-%m-%d %H:%M:%S'),
                        "is_in_period": is_in_period,
                        "days_from_start": (parsed_date - start_date).days
                    })
                except Exception as e:
                    data_analysis["first_5_records"].append({
                        "index": i,
                        "original": fecha_fichada,
                        "error": str(e)
                    })
            else:
                data_analysis["first_5_records"].append({
                    "index": i,
                    "original": str(fecha_fichada),
                    "type": type(fecha_fichada).__name__,
                    "is_in_period": "unknown"
                })
        
        # Paso 3: Probar el agrupamiento por día
        compliance_checker = ComplianceChecker(db_manager)
        daily_attendance = compliance_checker._group_by_day(attendance_data, start_date, end_date)
        
        # Paso 4: Analizar el resultado del agrupamiento
        grouping_analysis = {
            "total_days_found": len(daily_attendance),
            "day_keys": list(daily_attendance.keys()),
            "records_per_day": {day: len(records) for day, records in daily_attendance.items()}
        }
        
        return {
            "success": True,
            "employee_id": employee_id,
            "period": {
                "start": start_date.strftime('%Y-%m-%d %H:%M:%S'),
                "end": end_date.strftime('%Y-%m-%d %H:%M:%S'),
                "days": (end_date - start_date).days
            },
            "step_1_attendance_data": data_analysis,
            "step_2_daily_grouping": grouping_analysis,
            "debug_info": {
                "start_date_type": type(start_date).__name__,
                "end_date_type": type(end_date).__name__,
                "attendance_data_type": type(attendance_data).__name__
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "employee_id": employee_id,
            "traceback": str(e.__traceback__) if hasattr(e, '__traceback__') else "No traceback"
        }
