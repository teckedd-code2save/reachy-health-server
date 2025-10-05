from pydantic import BaseModel
from typing import Optional

class Case(BaseModel):
    id: Optional[int] = None
    patient_id: int
    visit_id: Optional[int] = None
    description: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
