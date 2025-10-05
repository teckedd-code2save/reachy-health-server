from pydantic import BaseModel
from typing import Optional

class Visit(BaseModel):
    id: Optional[int] = None
    patient_id: int
    visit_date: str
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
