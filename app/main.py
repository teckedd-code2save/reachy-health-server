from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(
    title="Intelligent File Management System",
    description="""
    Advanced API for intelligent file management with features including:
    - File processing and optimization
    - Content analysis and metadata extraction
    - Intelligent categorization and tagging
    - Advanced search capabilities
    - Version control and access management
    - Cloud storage integration
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Intelligent File Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    } 