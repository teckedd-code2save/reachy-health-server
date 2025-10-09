from sqlalchemy.orm import Session
from app.core.models import ConsultationDB, ChatMessageDB, FileAttachmentDB
from app.schemas.consultation import ConsultationCreate, ConsultationUpdate, ChatMessageCreate, FileAttachmentCreate
from typing import List, Optional

class ConsultationService:
    @staticmethod
    def create(db: Session, consultation: ConsultationCreate) -> ConsultationDB:
        db_consultation = ConsultationDB(**consultation.dict())
        db.add(db_consultation)
        db.commit()
        db.refresh(db_consultation)
        return db_consultation

    @staticmethod
    def get_all(db: Session, status: Optional[str] = None) -> List[ConsultationDB]:
        query = db.query(ConsultationDB)
        if status:
            query = query.filter(ConsultationDB.status == status)
        return query.order_by(ConsultationDB.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, consultation_id: int) -> Optional[ConsultationDB]:
        return db.query(ConsultationDB).filter(ConsultationDB.id == consultation_id).first()

    @staticmethod
    def update(db: Session, consultation_id: int, update: ConsultationUpdate) -> Optional[ConsultationDB]:
        db_consultation = ConsultationService.get_by_id(db, consultation_id)
        if not db_consultation:
            return None

        for key, value in update.dict(exclude_unset=True).items():
            setattr(db_consultation, key, value)

        db.commit()
        db.refresh(db_consultation)
        return db_consultation

class ChatMessageService:
    @staticmethod
    def create(db: Session, chat_message: ChatMessageCreate) -> ChatMessageDB:
        db_chat_message = ChatMessageDB(**chat_message.dict())
        db.add(db_chat_message)
        db.commit()
        db.refresh(db_chat_message)
        return db_chat_message

    @staticmethod
    def get_by_consultation_id(db: Session, consultation_id: int) -> List[ChatMessageDB]:
        return db.query(ChatMessageDB).filter(ChatMessageDB.consultation_id == consultation_id).order_by(ChatMessageDB.timestamp.asc()).all()

class FileAttachmentService:
    @staticmethod
    def create(db: Session, file_attachment: FileAttachmentCreate) -> FileAttachmentDB:
        db_file_attachment = FileAttachmentDB(**file_attachment.dict())
        db.add(db_file_attachment)
        db.commit()
        db.refresh(db_file_attachment)
        return db_file_attachment

    @staticmethod
    def get_by_consultation_id(db: Session, consultation_id: int) -> List[FileAttachmentDB]:
        return db.query(FileAttachmentDB).filter(FileAttachmentDB.consultation_id == consultation_id).order_by(FileAttachmentDB.uploaded_at.asc()).all()
