from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from app.application.services import JobService
from app.api.dependencies.services import get_job_service
from typing import Optional

router = APIRouter(prefix="/job", tags=["Job Description"])

@router.post("/upload")
async def upload_job_description(
    session_id: str = Form(...),
    file: Optional[UploadFile] = File(None),
    jd_text: Optional[str] = Form(None),
    job_service: JobService = Depends(get_job_service)
):
    """Upload target Job Description (as raw text or PDF)."""
    if not file and not jd_text:
        raise HTTPException(
            status_code=400, 
            detail="You must supply either a PDF file in the 'file' field or text in the 'jd_text' field"
        )

    file_bytes = None
    if file:
        file_bytes = await file.read()

    text = job_service.process_job_description(
        session_id=session_id,
        jd_text=jd_text,
        file_bytes=file_bytes
    )

    return {
        "message": "Job description parsed and indexed successfully",
        "session_id": session_id,
        "character_count": len(text)
    }
