import boto3
import os
from botocore.config import Config
from fastapi import UploadFile
from app.core.config import settings
import tempfile
from datetime import datetime

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file_key: str, file_content: bytes, content_type: str) -> str:
        """
        Upload a file to S3
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type
            )
            return await self.get_presigned_url(file_key)
        except Exception as e:
            raise Exception(f"Error uploading file: {str(e)}")

    async def get_presigned_url(self, file_key: str) -> str:
        """
        Generate a presigned URL for a file
        """
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=3600
            )
        except Exception as e:
            raise Exception(f"Error generating presigned URL: {str(e)}")

    async def list_files(self) -> list:
        """
        List all files in the bucket
        """
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        files = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': obj['Key']},
                    ExpiresIn=3600
                )
                files.append({
                    "filename": obj['Key'].strip(),
                    "url": url,
                    "size": obj['Size'],
                    "created_at": obj['LastModified'].isoformat()
                })
        
        return files

    async def download_file(self, file_key: str) -> str:
        """
        Download a file from S3
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                self.s3_client.download_fileobj(
                    self.bucket_name,
                    file_key,
                    temp_file
                )
                return temp_file.name
        except Exception as e:
            raise Exception(f"Error downloading file: {str(e)}")
        
    async def get_file_metadata(self, file_id: str) -> dict:
        """
        Get metadata of a file in S3
        """
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=file_id)
            return {
                "filename": file_id,
                "size": response['ContentLength'],
                "content_type": response['ContentType'],
                "last_modified": response['LastModified'].isoformat()
            }
        except Exception as e:
            raise Exception(f"Error retrieving file metadata: {str(e)}")

    async def delete_file(self, file_key: str) -> None:
        """
        Delete a file from S3
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
        except Exception as e:
            raise Exception(f"Error deleting file: {str(e)}") 
        
def sanitized(filename: str) -> str:
    # Remove all spaces and convert to lowercase
    return filename.replace(' ', '').lower()
