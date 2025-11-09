from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.schemas.consultation import (
    ConsultationCreate, ConsultationResponse, ConsultationUpdate,
    ChatMessageCreate, FileAttachmentCreate
)
from app.services.consultation import ConsultationService, ChatMessageService, FileAttachmentService
from app.services.file_processor import FileProcessor
from app.services.s3_service import S3Service
from app.services.file_processor import FileProcessor
from app.services.transcription_service import get_transcription_service
from typing import List, Optional
from datetime import datetime
import os

router = APIRouter()
s3_service = S3Service()
file_processor = FileProcessor()

@router.post("/", response_model=ConsultationResponse)
async def create_consultation(
    transcript: str = Form(...),
    language: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create consultation: {str(e)}")

@router.get("/", response_model=List[ConsultationResponse])
def list_consultations(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        return ConsultationService.get_all(db, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve consultations: {str(e)}")

@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(consultation_id: int, db: Session = Depends(get_db)):
    try:
        consultation = ConsultationService.get_by_id(db, consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")
        return consultation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve consultation: {str(e)}")

@router.put("/{consultation_id}", response_model=ConsultationResponse)
def update_consultation(
    consultation_id: int,
    update: ConsultationUpdate,
    db: Session = Depends(get_db)
):
    try:
        consultation = ConsultationService.update(db, consultation_id, update)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")
        return consultation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update consultation: {str(e)}")

# Chat message endpoints
@router.post("/{consultation_id}/chat", response_model=dict)
def add_chat_message(
    consultation_id: int,
    chat_message: ChatMessageCreate,
    db: Session = Depends(get_db)
):
    try:
        # Verify consultation exists
        consultation = ConsultationService.get_by_id(db, consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")

        # Update consultation's updated_at timestamp
        consultation.updated_at = datetime.utcnow()
        db.commit()

        # Create chat message
        ChatMessageService.create(db, chat_message)
        return {"message": "Chat message added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add chat message: {str(e)}")

@router.get("/{consultation_id}/chat", response_model=List[dict])
def get_chat_messages(consultation_id: int, db: Session = Depends(get_db)):
    try:
        # Verify consultation exists
        consultation = ConsultationService.get_by_id(db, consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")

        messages = ChatMessageService.get_by_consultation_id(db, consultation_id)
        return [
            {
                "id": msg.id,
                "sender": msg.sender,
                "message": msg.message,
                "message_type": msg.message_type,
                "timestamp": msg.timestamp
            }
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat messages: {str(e)}")

# File attachment endpoints
@router.post("/{consultation_id}/files", response_model=dict)
async def upload_file_to_consultation(
    consultation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Verify consultation exists
        consultation = ConsultationService.get_by_id(db, consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")

        # Upload file to S3
        file_content = await file.read()
        file_key = f"consultations/{consultation_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        file_url = await s3_service.upload_file(file_key, file_content, file.content_type)

        # Process file for metadata
        metadata = await file_processor.process_file(file.filename, file_content)

        # Create file attachment record
        file_attachment_data = FileAttachmentCreate(
            consultation_id=consultation_id,
            filename=file.filename,
            file_url=file_url,
            file_type=file.content_type or 'application/octet-stream',
            file_size=len(file_content)
        )

        # Update consultation's updated_at timestamp
        consultation.updated_at = datetime.utcnow()
        db.commit()

        FileAttachmentService.create(db, file_attachment_data)
        return {"message": "File uploaded successfully", "file_url": file_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.get("/{consultation_id}/files", response_model=List[dict])
def get_consultation_files(consultation_id: int, db: Session = Depends(get_db)):
    try:
        # Verify consultation exists
        consultation = ConsultationService.get_by_id(db, consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")

        files = FileAttachmentService.get_by_consultation_id(db, consultation_id)
        return [
            {
                "id": file.id,
                "filename": file.filename,
                "file_url": file.file_url,
                "file_type": file.file_type,
                "file_size": file.file_size,
                "uploaded_at": file.uploaded_at
            }
            for file in files
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve files: {str(e)}")

@router.post("/{consultation_id}/transcribe", response_model=dict)
async def transcribe_consultation_audio(
    consultation_id: int,
    db: Session = Depends(get_db)
):
    """
    Transcribe the audio recording for a consultation using Whisper model.
    Updates the consultation's transcript field.
    """
    try:
        # Verify consultation exists
        consultation = ConsultationService.get_by_id(db, consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")
        
        # Check if consultation has audio
        if not consultation.audio_url:
            raise HTTPException(status_code=400, detail="Consultation has no audio recording")
        
        # Download audio from S3 or fetch from URL
        # Try to download from S3 using the URL as a presigned URL
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(consultation.audio_url)
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail="Failed to download audio file")
                audio_content = response.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to download audio: {str(e)}")
        
        # Get transcription service
        transcription_service = get_transcription_service()
        
        # Determine audio format from URL or content type
        audio_format = "webm"  # Default, could be extracted from content_type
        if consultation.audio_url:
            if ".wav" in consultation.audio_url:
                audio_format = "wav"
            elif ".mp3" in consultation.audio_url:
                audio_format = "mp3"
            elif ".m4a" in consultation.audio_url:
                audio_format = "m4a"
        
        # Transcribe audio
        result = transcription_service.transcribe_bytes(audio_content, audio_format=audio_format)
        transcript_text = result.get("transcript", "")
        
        if not transcript_text:
            raise HTTPException(status_code=500, detail="Transcription returned empty result")
        
        # Update consultation with transcript
        consultation.transcript = transcript_text
        db.commit()
        db.refresh(consultation)
        
        return {
            "message": "Transcription completed successfully",
            "transcript": transcript_text,
            "consultation_id": consultation_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/transcribe", response_model=dict)
async def transcribe_audio_file(
    audio: UploadFile = File(...),
    detect_language: bool = Form(False)
):
    """
    Standalone transcription endpoint for audio files.
    Used for landing page voice transcription and language detection.
    
    Args:
        audio: Audio file to transcribe
        detect_language: Whether to attempt language detection (optional)
    """
    try:
        # Read audio file
        audio_content = await audio.read()
        
        # Get transcription service
        transcription_service = get_transcription_service()
        
        # Determine audio format
        audio_format = "webm"  # Default
        if audio.content_type:
            if "wav" in audio.content_type:
                audio_format = "wav"
            elif "mp3" in audio.content_type:
                audio_format = "mp3"
            elif "m4a" in audio.content_type or "mp4" in audio.content_type:
                audio_format = "m4a"
        elif audio.filename:
            ext = audio.filename.split('.')[-1].lower()
            if ext in ["wav", "mp3", "m4a", "mp4"]:
                audio_format = ext
        
        # Transcribe audio
        result = transcription_service.transcribe_bytes(audio_content, audio_format=audio_format)
        transcript_text = result.get("transcript", "")
        
        response = {
            "transcript": transcript_text,
            "text": transcript_text  # Alias for convenience
        }
        
        # Language detection (simplified - can be enhanced)
        if detect_language:
            # Basic language hints based on common words/phrases
            detected_lang = None
            text_lower = transcript_text.lower()
            # This is a placeholder - you might want to use a dedicated language detection model
            # or enhance the Whisper output parsing
            response["detected_language"] = detected_lang
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
