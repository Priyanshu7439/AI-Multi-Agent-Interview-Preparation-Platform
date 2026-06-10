import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.application.services import ResumeService
from app.api.dependencies.services import get_resume_service

router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    session_id: str = Form(None),
    resume_service: ResumeService = Depends(get_resume_service)
):
    """Upload candidate's resume PDF. Automatically parses and embeds content."""
    if not session_id or session_id.strip() == "":
        session_id = str(uuid.uuid4())
        
    file_bytes = await file.read()
    text = resume_service.process_resume(session_id, file_bytes)
    
    return {
        "message": "Resume uploaded and indexed successfully",
        "session_id": session_id,
        "filename": file.filename,
        "character_count": len(text)
    }
