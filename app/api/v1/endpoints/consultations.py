from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.schemas.consultation import ConsultationCreate, ConsultationResponse, ConsultationUpdate
from app.services.consultation.service import ConsultationService
from app.services.s3_service import S3Service
from typing import List, Optional
from datetime import datetime

router = APIRouter()
s3_service = S3Service()

@router.post("/", response_model=ConsultationResponse)
async def create_consultation(
    transcript: str = Form(...),
    language: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Upload audio to S3
    audio_content = await audio.read()
    audio_key = f"consultations/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{audio.filename}"
    audio_url = await s3_service.upload_file(audio_key, audio_content, audio.content_type or 'audio/webm')
    
    # Create consultation
    consultation_data = ConsultationCreate(
        transcript=transcript,
        language=language,
        audio_url=audio_url
    )
    
    consultation = ConsultationService.create(db, consultation_data)
    return consultation

@router.get("/", response_model=List[ConsultationResponse])
def list_consultations(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return ConsultationService.get_all(db, status)

@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(consultation_id: int, db: Session = Depends(get_db)):
    consultation = ConsultationService.get_by_id(db, consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return consultation

@router.put("/{consultation_id}", response_model=ConsultationResponse)
def update_consultation(
    consultation_id: int,
    update: ConsultationUpdate,
    db: Session = Depends(get_db)
):
    consultation = ConsultationService.update(db, consultation_id, update)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return consultation
