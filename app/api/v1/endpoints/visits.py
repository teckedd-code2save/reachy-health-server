from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.models import VisitDB
from app.schemas.visit import Visit
from typing import List

router = APIRouter()

@router.post("/", response_model=Visit)
def create_visit(visit: Visit, db: Session = Depends(get_db)):
    db_visit = VisitDB(**visit.dict())
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit

@router.get("/", response_model=List[Visit])
def list_visits(db: Session = Depends(get_db)):
    return db.query(VisitDB).all()

@router.get("/{visit_id}", response_model=Visit)
def get_visit(visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(VisitDB).get(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit

@router.put("/{visit_id}", response_model=Visit)
def update_visit(visit_id: int, visit: Visit, db: Session = Depends(get_db)):
    db_visit = db.query(VisitDB).get(visit_id)
    if not db_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    for key, value in visit.dict().items():
        setattr(db_visit, key, value)
    db.commit()
    db.refresh(db_visit)
    return db_visit

@router.delete("/{visit_id}")
def delete_visit(visit_id: int, db: Session = Depends(get_db)):
    db_visit = db.query(VisitDB).get(visit_id)
    if not db_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    db.delete(db_visit)
    db.commit()
    return {"message": "Visit deleted"}
