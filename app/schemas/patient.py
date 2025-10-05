from pydantic import BaseModel
from typing import Optional

class Patient(BaseModel):
    id: Optional[int] = None
    name: str
    age: int
    gender: str
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
