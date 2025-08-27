from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

class Employee(BaseModel):
    id: int
    name: str
    department: str
    attendance_days: int

# Temporal hasta conectar a Oracle
_FAKE = [
    Employee(id=1, name="Juan Pérez", department="IT", attendance_days=4),
    Employee(id=2, name="María Gómez", department="HR", attendance_days=2),
]

@router.get("/employees", response_model=List[Employee])
def list_employees(
    department: Optional[str] = Query(None),
    min_days: Optional[int] = Query(None, ge=0)
):
    data = _FAKE
    if department:
        data = [e for e in data if e.department.lower() == department.lower()]
    if min_days is not None:
        data = [e for e in data if e.attendance_days >= min_days]
    return data