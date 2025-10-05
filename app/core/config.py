from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os
import getpass

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Intelligent File Management System"
    
    # S3 Configuration
    S3_ENDPOINT_URL: str = "http://localhost:4566"  # LocalStack default endpoint
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "file-management"
    
    # File Processing Configuration
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "application/pdf",
        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain", "video/mp4", "audio/mpeg"
    ]
    
    # Search Configuration
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "fileverse"
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OCR Configuration
    ENABLE_OCR: bool = True
    OCR_LANGUAGE: str = "eng"
    
    # Cache Configuration
    REDIS_URL: str = "redis://localhost:6379"

    # Chat models api keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "your-xai-api-key")
    MIsTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "your-mistral-api-key")
    
    #search and chat models
    # Use a Hugging Face model repo id for semantic search (e.g., 'sentence-transformers/all-MiniLM-L6-v2')
    SEMANTIC_SEARCH_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    # Hugging Face Hub API token for private or rate-limited models
    HUGGINGFACEHUB_API_TOKEN: str = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 