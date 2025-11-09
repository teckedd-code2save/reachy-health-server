# # ==========================================
# # app/api/consultation_summary.py
# # FastAPI Router for Consultation Summaries
# # ==========================================

# from fastapi import APIRouter, HTTPException, Depends, Response
# from fastapi.responses import StreamingResponse
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from datetime import datetime
# import json
# import io

# from app.db.session import get_db
# from app.models.consultation import Consultation, ChatMessage
# from app.services.agentic.medical_rag_service import MedicalRAGService
# from pydantic import BaseModel

# router = APIRouter()

# # Pydantic Models
# class MedicalEntities(BaseModel):
#     symptoms: List[str] = []
#     diagnoses: List[str] = []
#     medications: List[str] = []

# class ConsultationSummary(BaseModel):
#     consultation_id: int
#     summary: str
#     key_points: List[str]
#     medical_entities: MedicalEntities
#     sentiment: str
#     generated_at: str

# # Initialize RAG service globally
# medical_rag = None

# @router.on_event("startup")
# async def startup():
#     """Initialize medical RAG service on startup"""
#     global medical_rag
#     medical_rag = MedicalRAGService()
#     print("✅ Medical RAG Service initialized")

# @router.post("/consultations/{consultation_id}/summary", response_model=ConsultationSummary)
# async def generate_consultation_summary(
#     consultation_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Generate AI-powered summary for a consultation session.
#     This endpoint analyzes the conversation and extracts:
#     - Overall summary
#     - Key medical points
#     - Symptoms, diagnoses, and medications mentioned
#     - Sentiment analysis
#     """
#     # Fetch consultation
#     consultation = db.query(Consultation).filter(
#         Consultation.id == consultation_id
#     ).first()
    
#     if not consultation:
#         raise HTTPException(status_code=404, detail="Consultation not found")
    
#     # Fetch all messages
#     messages = db.query(ChatMessage).filter(
#         ChatMessage.consultation_id == consultation_id
#     ).order_by(ChatMessage.timestamp).all()
    
#     if not messages or len(messages) == 0:
#         raise HTTPException(
#             status_code=400, 
#             detail="No messages found. Cannot generate summary for empty consultation."
#         )
    
#     try:
#         # Prepare messages for RAG
#         message_data = [{
#             "sender": msg.sender,
#             "message": msg.message,
#             "timestamp": msg.timestamp.isoformat() if msg.timestamp else ""
#         } for msg in messages]
        
#         # Patient context
#         patient_context = {
#             "language": consultation.language if hasattr(consultation, 'language') else 'en',
#             "created_at": consultation.created_at.isoformat() if consultation.created_at else ""
#         }
        
#         # Generate summary using RAG
#         summary_data = await medical_rag.generate_conversation_summary(
#             consultation_id=consultation_id,
#             messages=message_data,
#             patient_context=patient_context
#         )
        
#         # Store summary in database
#         consultation.summary = json.dumps(summary_data)
#         consultation.updated_at = datetime.utcnow()
#         db.commit()
        
#         return ConsultationSummary(**summary_data)
        
#     except Exception as e:
#         db.rollback()
#         print(f"❌ Error generating summary: {str(e)}")
#         raise HTTPException(
#             status_code=500, 
#             detail=f"Failed to generate summary: {str(e)}"
#         )

# @router.get("/consultations/{consultation_id}/summary", response_model=ConsultationSummary)
# async def get_consultation_summary(
#     consultation_id: int,
#     db: Session = Depends(get_db)
# ):
#     """
#     Retrieve existing summary for a consultation.
#     Returns 404 if no summary has been generated yet.
#     """
#     consultation = db.query(Consultation).filter(
#         Consultation.id == consultation_id
#     ).first()
    
#     if not consultation:
#         raise HTTPException(status_code=404, detail="Consultation not found")
    
#     if not consultation.summary:
#         raise HTTPException(
#             status_code=404, 
#             detail="No summary found. Generate one first by calling POST /consultations/{id}/summary"
#         )
    
#     try:
#         summary_data = json.loads(consultation.summary)
#         return ConsultationSummary(**summary_data)
#     except json.JSONDecodeError:
#         raise HTTPException(
#             status_code=500,
#             detail="Invalid summary data. Please regenerate the summary."
#         )

