from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.models import CaseDB
from app.schemas.case import Case
from typing import List

router = APIRouter()

@router.post("/", response_model=Case)
def create_case(case: Case, db: Session = Depends(get_db)):
    db_case = CaseDB(**case.dict())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

@router.get("/", response_model=List[Case])
def list_cases(db: Session = Depends(get_db)):
    return db.query(CaseDB).all()

@router.get("/{case_id}", response_model=Case)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(CaseDB).get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.put("/{case_id}", response_model=Case)
def update_case(case_id: int, case: Case, db: Session = Depends(get_db)):
    db_case = db.query(CaseDB).get(case_id)
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    for key, value in case.dict().items():
        setattr(db_case, key, value)
    db.commit()
    db.refresh(db_case)
    return db_case

@router.delete("/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    db_case = db.query(CaseDB).get(case_id)
    if not db_case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(db_case)
    db.commit()
    return {"message": "Case deleted"}
