from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.models import AlertDB
from app.schemas.alert import Alert
from typing import List

router = APIRouter()

@router.post("/", response_model=Alert)
def create_alert(alert: Alert, db: Session = Depends(get_db)):
    db_alert = AlertDB(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/", response_model=List[Alert])
def list_alerts(db: Session = Depends(get_db)):
    return db.query(AlertDB).all()

@router.get("/{alert_id}", response_model=Alert)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(AlertDB).get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.put("/{alert_id}", response_model=Alert)
def update_alert(alert_id: int, alert: Alert, db: Session = Depends(get_db)):
    db_alert = db.query(AlertDB).get(alert_id)
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    for key, value in alert.dict().items():
        setattr(db_alert, key, value)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    db_alert = db.query(AlertDB).get(alert_id)
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(db_alert)
    db.commit()
    return {"message": "Alert deleted"}
