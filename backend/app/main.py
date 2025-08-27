from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
import json
import os
from db.database_manager import DatabaseManager
from models.models import AttendanceStats, DataQualityIssue, MonthlyReport
from services.attendance_analyzer import AttendanceAnalyzer
from services.report_generator import ReportGenerator
from api.routes import employees
from core.config import settings

app = FastAPI(title="Office Attendance")

app.include_router(employees.router, prefix="/api", tags=["Employees"])

@app.get("/health")
def health():
    return {"status": "ok"}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
analyzer = AttendanceAnalyzer(db_manager)
report_generator = ReportGenerator(db_manager, analyzer)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await db_manager.connect()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await db_manager.disconnect()

@app.get("/")
async def root():
    return {"message": "Employee Attendance Dashboard API"}

@app.get("/api/employees", response_model=List[Dict[str, Any]])
async def get_employees():
    """Get all employees"""
    try:
        employees = await db_manager.get_all_employees()
        return employees
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/{employee_id}")
async def get_employee_attendance(
    employee_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get attendance records for a specific employee"""
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        attendance = await db_manager.get_employee_attendance(
            employee_id, start_date, end_date
        )
        return attendance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monthly-compliance/{year}/{month}")
async def get_monthly_compliance(year: int, month: int):
    """Get monthly compliance report for all employees"""
    try:
        report = await analyzer.generate_monthly_compliance_report(year, month)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/employee-stats/{employee_id}/{year}/{month}")
async def get_employee_monthly_stats(employee_id: int, year: int, month: int):
    """Get detailed monthly statistics for a specific employee"""
        from api.routes.employees import router as employees_router
        stats = await analyzer.analyze_employee_month(employee_id, year, month)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        app.include_router(employees_router, prefix="/api", tags=["Employees"])
@app.get("/api/data-quality-issues")
async def get_data_quality_issues(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Get data quality issues (missing exits, etc.)"""
    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        issues = await analyzer.detect_data_quality_issues(start_date, end_date)
        return issues
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard-stats")
async def get_dashboard_stats():
    """Get general dashboard statistics"""
    try:
        current_month = datetime.now()
        stats = await analyzer.get_dashboard_statistics(
            current_month.year, 
            current_month.month
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weekly-patterns/{employee_id}/{year}/{month}")
async def get_weekly_patterns(employee_id: int, year: int, month: int):
    """Get weekly attendance patterns for an employee"""
    try:
        patterns = await analyzer.analyze_weekly_patterns(employee_id, year, month)
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/monthly-report/{year}/{month}")
async def export_monthly_report(year: int, month: int):
    """Export monthly compliance report as Excel"""
    try:
        file_path = await report_generator.generate_excel_report(year, month)
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"attendance_report_{year}_{month:02d}.xlsx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends/{employee_id}")
async def get_employee_trends(
    employee_id: int,
    months_back: int = Query(6, description="Number of months to look back")
):
    """Get attendance trends for an employee over multiple months"""
    try:
        trends = await analyzer.get_employee_trends(employee_id, months_back)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/department-stats/{year}/{month}")
async def get_department_stats(year: int, month: int):
    """Get department-wise attendance statistics"""
    try:
        stats = await analyzer.get_department_statistics(year, month)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)