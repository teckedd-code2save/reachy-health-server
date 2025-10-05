from pydantic import BaseModel
from typing import Optional

class Alert(BaseModel):
    id: Optional[int] = None
    patient_id: int
    case_id: Optional[int] = None
    alert_type: str
    message: str
    severity: str
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None
