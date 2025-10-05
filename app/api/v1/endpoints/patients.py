from fastapi import APIRouter, HTTPException
from app.schemas.patient import Patient
from typing import List

router = APIRouter()

# In-memory store for demo purposes
patients_db = {}
next_id = 1

@router.post("/", response_model=Patient)
def create_patient(patient: Patient):
    global next_id
    patient.id = next_id
    patients_db[next_id] = patient
    next_id += 1
    return patient

@router.get("/", response_model=List[Patient])
def list_patients():
    return list(patients_db.values())

@router.get("/{patient_id}", response_model=Patient)
def get_patient(patient_id: int):
    patient = patients_db.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.put("/{patient_id}", response_model=Patient)
def update_patient(patient_id: int, patient: Patient):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient.id = patient_id
    patients_db[patient_id] = patient
    return patient

@router.delete("/{patient_id}")
def delete_patient(patient_id: int):
    if patient_id not in patients_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    del patients_db[patient_id]
    return {"message": "Patient deleted"}
