import os
import boto3
import magic
from fastapi import UploadFile, HTTPException, status
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()

class S3Service:
    def __init__(self):
        self.aws_access_key_id = settings.storage.aws_access_key_id
        self.aws_secret_access_key = settings.storage.aws_secret_access_key
        self.bucket_name = settings.storage.s3_bucket_name
        self.region = settings.storage.aws_region
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region
        )

    async def upload_file(self, upload_file: UploadFile, folder: str = "resumes") -> str:
        """
        Upload a file to S3 bucket
        Returns the S3 URL of the uploaded file
        """
        try:
            # Read file content
            content = await upload_file.read()
            
            # Check file type using python-magic
            file_type = magic.from_buffer(content, mime=True)
            if not file_type.startswith('application/pdf'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only PDF files are allowed"
                )
            
            # Generate unique filename
            filename = f"{folder}/{os.urandom(8).hex()}_{upload_file.filename}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=content,
                ContentType=file_type
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
            logger.info(f"File uploaded successfully to S3: {url}")
            return url
            
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to S3"
            )
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file"
            )
        finally:
            await upload_file.seek(0)

    async def delete_file(self, file_url: str) -> None:
        """
        Delete a file from S3 bucket using its URL
        """
        try:
            # Extract key from URL
            key = file_url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/")[1]
            
            # Delete from S3
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"File deleted successfully from S3: {file_url}")
            
        except Exception as e:
            logger.error(f"Error deleting file from S3: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file from S3"
            )

s3_service = S3Service()