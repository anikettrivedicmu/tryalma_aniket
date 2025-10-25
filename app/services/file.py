import os
import uuid
from datetime import datetime
from fastapi import HTTPException, UploadFile
import aiofiles
from app.core.config import settings

ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}

import os
import uuid
from fastapi import UploadFile, HTTPException, status
import aiofiles

from app.core.config import settings
from app.core.logging import get_logger
from app.services.s3 import s3_service

logger = get_logger()

async def save_resume(file: UploadFile) -> str:
    """
    Save a resume file to either local storage or S3
    Returns the path/url where the file was saved
    """
    try:
        # Verify file size
        content = await file.read()
        if len(content) > settings.storage.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )
        await file.seek(0)

        # Choose storage method based on configuration
        if settings.storage.storage_type == "s3":
            return await s3_service.upload_file(file)
        else:
            # Generate unique filename for local storage
            filename = f"{uuid.uuid4()}_{file.filename}"
            filepath = os.path.join(settings.storage.upload_dir, filename)
            
            # Save file locally
            async with aiofiles.open(filepath, 'wb') as out_file:
                await out_file.write(content)
            
            return filepath
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the file"
        )

async def delete_resume(file_path: str) -> None:
    """
    Delete a resume file from either local storage or S3
    """
    try:
        if settings.storage.storage_type == "s3":
            await s3_service.delete_file(file_path)
        else:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted successfully: {file_path}")
            else:
                logger.warning(f"File not found for deletion: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete the file"
        )

async def delete_resume(filepath: str) -> None:
    """
    Delete a resume file.
    """
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Could not delete file: {str(e)}"
            )