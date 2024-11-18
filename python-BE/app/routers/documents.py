from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import os
from app.services.document_parser import parse_document
from app.services.storage_service import upload_to_s3
import logging

# Initialize logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("./uploads", exist_ok=True)
        
        # Validate file
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
            
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file provided")
            
        # Create file path and save file
        file_path = os.path.join("./uploads", file.filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
            
        try:
            # Parse document (if needed)
            parsed_text = parse_document(file_path)
            
            # Upload to S3
            bucket_name = 'documentmanagementbucket'
            upload_to_s3(file_path, bucket_name, file.filename)
            
            # Clean up local file after upload
            os.remove(file_path)
            
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "File uploaded successfully",
                    "filename": file.filename
                }
            )
            
        except Exception as e:
            # Clean up file in case of error
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Error processing file: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))