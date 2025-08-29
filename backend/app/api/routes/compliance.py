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
