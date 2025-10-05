from fastapi import APIRouter
from app.api.v1.endpoints import files
from app.api.v1.endpoints import rag
from app.api.v1.endpoints import patients
from app.api.v1.endpoints import visits
from app.api.v1.endpoints import cases
from app.api.v1.endpoints import alerts
from app.api.v1.endpoints import consultations

api_router = APIRouter()
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(consultations.router, prefix="/consultations", tags=["consultations"])