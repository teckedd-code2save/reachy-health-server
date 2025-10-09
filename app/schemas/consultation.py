from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessage(BaseModel):
    id: Optional[int] = None
    sender: str  # 'patient' or 'doctor'
    message: str
    timestamp: datetime
    message_type: str = 'text'  # 'text', 'file', 'voice'

class FileAttachment(BaseModel):
    id: Optional[int] = None
    filename: str
    file_url: str
    file_type: str
    file_size: int
    uploaded_at: datetime

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
    doctor_response: Optional[str]
    chat_messages: List[ChatMessage] = []
    file_attachments: List[FileAttachment] = []
    created_at: datetime
    updated_at: datetime

class ConsultationUpdate(BaseModel):
    status: Optional[str] = None
    doctor_response: Optional[str] = None

class ChatMessageCreate(BaseModel):
    consultation_id: int
    sender: str
    message: str
    message_type: str = 'text'

class FileAttachmentCreate(BaseModel):
    consultation_id: int
    filename: str
    file_url: str
    file_type: str
    file_size: int
