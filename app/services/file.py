import os
import uuid
from datetime import datetime
from fastapi import HTTPException, UploadFile
import aiofiles
from app.core.config import settings

ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}

async def save_resume(file: UploadFile) -> str:
    """
    Save an uploaded resume file with a unique name.
    Returns the path where the file was saved.
    """
    # Validate file size
    if len(await file.read()) > settings.storage.max_file_size:
        raise HTTPException(status_code=400, detail="File too large")
    await file.seek(0)  # Reset file pointer after reading
    
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{timestamp}_{unique_id}{ext}"
    
    # Create full path
    filepath = os.path.join(settings.storage.upload_dir, filename)
    
    # Save file
    try:
        async with aiofiles.open(filepath, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save file: {str(e)}"
        )
    
    return filepath

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