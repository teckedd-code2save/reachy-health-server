from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ConsultationCreate(BaseModel):
    patient_id: Optional[int] = None
    transcript: str
    language: str
    audio_url: Optional[str] = None

class ConsultationResponse(BaseModel):
    id: int
    patient_id: Optional[int]
    transcript: str
    language: str
    audio_url: Optional[str]
    status: str
    created_at: datetime
    
class ConsultationUpdate(BaseModel):
    status: Optional[str] = None
    doctor_response: Optional[str] = None
