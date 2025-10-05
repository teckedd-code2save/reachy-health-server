from typing import Dict, Any, Optional
import magic
import os
from PIL import Image
import pytesseract
from app.core.config import settings
import boto3
from botocore.exceptions import ClientError
import logging
import io

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    async def process_file(self, file_path: str, file_content: bytes) -> Dict[str, Any]:
        """
        Process a file and extract relevant information
        """
        try:
            # Detect file type
            file_type = magic.from_buffer(file_content, mime=True)
            
            # Validate file type
            if file_type not in settings.ALLOWED_FILE_TYPES:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, file_content, file_type)
            
            # Process based on file type
            if file_type.startswith('image/'):
                metadata.update(self._process_image(file_content))
            elif file_type == 'application/pdf':
                metadata.update(self._process_pdf(file_content))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            raise

    def _extract_metadata(self, file_path: str, file_content: bytes, file_type: str) -> Dict[str, Any]:
        """
        Extract basic metadata from file
        """
        return {
            "filename": os.path.basename(file_path),
            "file_type": file_type,
            "size": len(file_content),
            "extension": os.path.splitext(file_path)[1].lower()
        }

    def _process_image(self, file_content: bytes) -> Dict[str, Any]:
        """
        Process image files
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            metadata = {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode
            }
            
            # Perform OCR if enabled
            if settings.ENABLE_OCR:
                text = pytesseract.image_to_string(image, lang=settings.OCR_LANGUAGE)
                metadata["ocr_text"] = text
            
            return metadata
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {}

    def _process_pdf(self, file_content: bytes) -> Dict[str, Any]:
        """
        Process PDF files
        """
        # TODO: Implement PDF processing
        return {}

    async def upload_to_s3(self, file_path: str, file_content: bytes, metadata: Dict[str, Any]) -> str:
        """
        Upload file to S3 with metadata
        """
        try:
            key = f"uploads/{metadata['filename']}"
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key,
                Body=file_content,
                Metadata=metadata
            )
            return key
        except ClientError as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise 