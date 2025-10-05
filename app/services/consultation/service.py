from sqlalchemy.orm import Session
from app.core.models import ConsultationDB
from app.schemas.consultation import ConsultationCreate, ConsultationUpdate
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
