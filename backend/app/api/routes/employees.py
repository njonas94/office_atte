from typing import List, Optional
from fastapi import APIRouter, Query
from app.db.database_manager import DatabaseManager
from app.models.models import EmployeeInfo

router = APIRouter()
db_manager = DatabaseManager()

@router.get("/search", response_model=List[EmployeeInfo])
async def search_personas(
    ids: Optional[List[int]] = Query(None, description="IDs de personas"),
    apellido: Optional[str] = Query(None, description="Apellido (puede ser parcial)")
):
    """
    Buscar personas por ID(s) y/o Apellido (parcial).
    """
    query = "SELECT ID_PERSONA, NOMBRE, APELLIDO, DEPARTAMENTO, EMAIL FROM CRONOS.PERSONA WHERE 1=1"
    params = {}
    if ids:
        query += " AND ID_PERSONA IN ({})".format(','.join([f":id{i}" for i in range(len(ids))]))
        for i, id_val in enumerate(ids):
            params[f"id{i}"] = id_val
    if apellido:
        query += " AND LOWER(APELLIDO) LIKE :apellido"
        params["apellido"] = f"%{apellido.lower()}%"
    # Conexión y consulta
    await db_manager.connect()
    cursor = db_manager.connection.cursor()
    cursor.execute(query, params)
    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    await db_manager.disconnect()
    return [EmployeeInfo(**row) for row in rows]