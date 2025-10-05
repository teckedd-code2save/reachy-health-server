from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import List
from app.services.s3_service import S3Service
from app.services.file_processor import FileProcessor
from app.services.semantic_search_service import SemanticSearchService
from app.schemas.file import FileResponse as FileResponseSchema
from datetime import datetime

router = APIRouter()
s3_service = S3Service()
file_processor = FileProcessor()
semantic_search_service = SemanticSearchService()

@router.post("/upload", response_model=FileResponseSchema)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to S3 storage, process it, and store metadata.
    """
    try:
        file_content = await file.read()
        file_key = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        # Process file to extract metadata and OCR
        metadata = await file_processor.process_file(file.filename, file_content)
        
        # Upload file to S3
        file_url = await s3_service.upload_file(file_key, file_content, file.content_type)
        
        # Index file with semantic embedding
        await semantic_search_service.index_file({
            "id": file_key,
            "filename": file.filename,
            "content_type": file.content_type,
            **metadata
        })
        
        # Add metadata to the response
        return {
            "filename": file.filename.strip(),
            "url": file_url,
            "content_type": file.content_type,
            **metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/presigned-url/{file_key}")
async def get_presigned_url(file_key: str):
    """
    Get a presigned URL for a file
    """
    try:
        url = await s3_service.get_presigned_url(file_key)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")

@router.get("/semantic-search", response_model=List[FileResponseSchema])
async def semantic_search_files(query: str, top_k: int = 10):
    """
    Perform semantic search for files
    """
    try:
        files = await semantic_search_service.semantic_search(query, top_k)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[FileResponseSchema])
async def search_files(query: str="", page: int = 1, size: int = 10):
    """
    List all files in the S3 bucket
    """
    try:
        files = await s3_service.list_files()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_key}")
async def download_file(file_key: str):
    """
    Download a file from S3 storage
    """
    try:
        file_data = await s3_service.download_file(file_key)
        return FileResponse(
            file_data,
            media_type="application/octet-stream",
            filename=file_key
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")

@router.delete("/{file_key}")
async def delete_file(file_key: str):
    """
    Delete a file from S3 storage
    """
    try:
        await s3_service.delete_file(file_key)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")



@router.get("/{file_id}")
async def get_file(file_id: str):
    try:
        return await s3_service.get_file_metadata(file_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="File not found")

@router.delete("/{file_id}")
async def delete_file_index(file_id: str):
    try:
        await s3_service.delete_index(file_id)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    