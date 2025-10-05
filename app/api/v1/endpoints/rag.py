from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.services.agentic.rag_pipeline_service import RAGPipeline
from app.schemas.agentic import RAGConfig, RAGResponse, DocumentLoaderConfig
import boto3
import aiohttp
import os

router = APIRouter()
# Pydantic models for request bodies
class TextInput(BaseModel):
    content: str

class WebInput(BaseModel):
    url: str
    selector: Optional[str] = "p"

class FileInput(BaseModel):
    presigned_url: str

class QueryRequest(BaseModel):
    question: str

# Initialize RAG pipeline (assuming config is predefined or loaded from environment)
config = RAGConfig(
    llm={"model": "mistral-large-latest", "temperature": 0},
    embeddings={"provider":"mistralai","model": "mistral-embed"},
    chunking={"chunkSize": 1000, "chunkOverlap": 200},
    vectorStore={"type": "memory"},
    documentLoader={"type": "web", "webConfig": {"url": "https://lilianweng.github.io/posts/2023-06-23-agent/", "selector": "p"}}
)
rag_pipeline = None

@router.on_event("startup")
async def startup_event():
    global rag_pipeline
    rag_pipeline = RAGPipeline(config)
    await rag_pipeline.initialize()

@router.post("/query", response_model=RAGResponse)
async def query_pipeline(request: QueryRequest):
    """
    Query the RAG pipeline with a question.
    """
    try:
        response = await rag_pipeline.query(request.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.post("/add/text")
async def add_text_document(text_input: TextInput):
    """
    Add a text document to the RAG pipeline.
    """
    try:
        doc_config = DocumentLoaderConfig(type="text", textConfig={"content": text_input.content})
        await rag_pipeline.add_new_documents(doc_config)
        return {"message": "Text document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add text document: {str(e)}")

@router.post("/add/web")
async def add_web_document(web_input: WebInput):
    """
    Add a web document to the RAG pipeline.
    """
    try:
        doc_config = DocumentLoaderConfig(type="web", webConfig={"url": web_input.url, "selector": web_input.selector})
        await rag_pipeline.add_new_documents(doc_config)
        return {"message": "Web document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add web document: {str(e)}")

@router.post("/add/file")
async def add_file_document(file_input: FileInput):
    """
    Add a document from an S3 presigned URL to the RAG pipeline.
    """
    try:
        # Fetch file content from presigned URL
        async with aiohttp.ClientSession() as session:
            async with session.get(file_input.presigned_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch file from presigned URL")
                content = await response.text()
        
        doc_config = DocumentLoaderConfig(type="text", textConfig={"content": content})
        await rag_pipeline.add_new_documents(doc_config)
        return {"message": "File document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add file document: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API status.
    """
    return {"status": "healthy"}