import cx_Oracle
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import pandas as pd
import redis
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
        self.cache_ttl = 300  # 5 minutes cache
        
    async def connect(self):
        """Establish connection to Oracle database"""
        try:
            dsn = cx_Oracle.makedsn(
                host=os.getenv('ORACLE_HOST'),
                port=os.getenv('ORACLE_PORT', 1521),
                service_name=os.getenv('ORACLE_SERVICE_NAME')
            )
            
            self.connection = cx_Oracle.connect(
                user=os.getenv('ORACLE_USER'),
                password=os.getenv('ORACLE_PASSWORD'),
                dsn=dsn,
                encoding="UTF-8"
            )
            logger.info("Connected to Oracle database successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def _get_cache_key(self, operation: str, **kwargs) -> str:
        """Generate cache key for operations"""
        params = "_".join([f"{k}_{v}" for k, v in sorted(kwargs.items())])
        return f"{operation}_{params}"
    
    def _cache_get(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        return None
    
    def _cache_set(self, key: str, data: Any, ttl: int = None):
        """Set data in cache"""
        try:
            ttl = ttl or self.cache_ttl
            self.redis_client.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    async def get_all_employees(self) -> List[Dict[str, Any]]:
        """Get all employees from the employee table"""
        cache_key = self._get_cache_key("employees")
        cached_data = self._cache_get(cache_key)
        if cached_data:
            return cached_data
        
        query = """
        SELECT ID_PERSONA, NOMBRE, APELLIDO, EMAIL
        FROM CRONOS.PERSONA 
        ORDER BY APELLIDO, NOMBRE
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            columns = [col[0] for col in cursor.description]
            employees = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            
            # Cache for longer since employee data doesn't change often
            self._cache_set(cache_key, employees, ttl=3600)
            return employees
            
        except Exception as e:
            logger.error(f"Error fetching employees: {e}")
            raise
    
    async def get_employee_attendance(
        self, 
        employee_id: int, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get attendance records for a specific employee"""
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        cache_key = self._get_cache_key(
            "attendance", 
            employee_id=employee_id, 
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d")
        )
        
        cached_data = self._cache_get(cache_key)
        if cached_data:
            return cached_data
        
        query = """
        SELECT ID_PERSONA, FECHA_FICHADA, PRIORIDAD, IGNORAR
        FROM CRONOS.FICHADA_PROCESO 
        WHERE ID_PERSONA = :employee_id 
        AND FECHA_FICHADA >= :start_date 
        AND FECHA_FICHADA <= :end_date
        AND (IGNORAR = 0 OR IGNORAR IS NULL)
        ORDER BY FECHA_FICHADA
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, {
                'employee_id': employee_id,
                'start_date': start_date,
                'end_date': end_date
            })
            
            columns = [col[0] for col in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            
            self._cache_set(cache_key, records)
            return records
            
        except Exception as e:
            logger.error(f"Error fetching attendance for employee {employee_id}: {e}")
            raise
    
    async def get_monthly_attendance_all_employees(
        self, 
        year: int, 
        month: int
    ) -> List[Dict[str, Any]]:
        """Get all attendance records for a specific month"""
        
        cache_key = self._get_cache_key("monthly_all", year=year, month=month)
        cached_data = self._cache_get(cache_key)
        if cached_data:
            return cached_data
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        query = """
        SELECT ID_PERSONA, FECHA_FICHADA, PRIORIDAD, IGNORAR
        FROM CRONOS.FICHADA_PROCESO 
        WHERE FECHA_FICHADA >= :start_date 
        AND FECHA_FICHADA <= :end_date
        AND (IGNORAR = 0 OR IGNORAR IS NULL)
        ORDER BY ID_PERSONA, FECHA_FICHADA
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, {
                'start_date': start_date,
                'end_date': end_date
            })
            
            columns = [col[0] for col in cursor.description]
            records = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            
            # Cache for longer for historical months
            current_date = datetime.now()
            is_current_month = (year == current_date.year and month == current_date.month)
            cache_ttl = 300 if is_current_month else 3600
            
            self._cache_set(cache_key, records, ttl=cache_ttl)
            return records
            
        except Exception as e:
            logger.error(f"Error fetching monthly attendance for {year}-{month}: {e}")
            raise
    
    async def get_employee_info(self, employee_id: int) -> Optional[Dict[str, Any]]:
        """Get employee information by ID"""
        cache_key = self._get_cache_key("employee_info", employee_id=employee_id)
        cached_data = self._cache_get(cache_key)
        if cached_data:
            return cached_data
        
        query = """
        SELECT ID_PERSONA, NOMBRE, APELLIDO, EMAIL
        FROM CRONOS.PERSONA 
        WHERE ID_PERSONA = :employee_id
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, {'employee_id': employee_id})
            
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                employee_info = dict(zip(columns, row))
                
                cursor.close()
                
                # Cache employee info for longer since it rarely changes
                self._cache_set(cache_key, employee_info, ttl=3600)
                return employee_info
            
            cursor.close()
            return None
            
        except Exception as e:
            logger.error(f"Error fetching employee info for {employee_id}: {e}")
            raise
    
    async def get_data_quality_issues(
        self, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Detect data quality issues like missing exits"""
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Query to find days with odd number of records (missing entry or exit)
        query = """
        SELECT 
            ID_PERSONA,
            TRUNC(FECHA_FICHADA) as DIA,
            COUNT(*) as TOTAL_REGISTROS,
            MIN(FECHA_FICHADA) as PRIMER_REGISTRO,
            MAX(FECHA_FICHADA) as ULTIMO_REGISTRO
        FROM CRONOS.FICHADA_PROCESO 
        WHERE FECHA_FICHADA >= :start_date 
        AND FECHA_FICHADA <= :end_date
        AND (IGNORAR = 0 OR IGNORAR IS NULL)
        GROUP BY ID_PERSONA, TRUNC(FECHA_FICHADA)
        HAVING COUNT(*) != 2
        ORDER BY FECHA_FICHADA DESC, ID_PERSONA
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, {
                'start_date': start_date,
                'end_date': end_date
            })
            
            columns = [col[0] for col in cursor.description]
            issues = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            cursor.close()
            return issues
            
        except Exception as e:
            logger.error(f"Error detecting data quality issues: {e}")
            raise