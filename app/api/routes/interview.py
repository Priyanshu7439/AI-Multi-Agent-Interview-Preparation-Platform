from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.application.services import InterviewService
from app.api.dependencies.services import get_interview_service
from typing import Dict, Any

router = APIRouter(tags=["Interview Preparation Flow"])

class SessionRequest(BaseModel):
    session_id: str = Field(..., description="Unique session ID of the candidate preparation flow")

class AnswerRequest(BaseModel):
    session_id: str = Field(..., description="Unique session ID")
    question_id: str = Field(..., description="The ID of the question being answered")
    answer_text: str = Field(..., description="Candidate's transcript/text response to the question")

@router.post("/analyze", response_model=Dict[str, str])
async def analyze_session(
    request: SessionRequest,
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Trigger the multi-agent analysis loop. Parses resume/JD, conducts gap analysis, and generates questions."""
    try:
        # Create session in repository if not already created
        # (Usually created during resume/job upload, but this guarantees it exists)
        interview_service.create_session(request.session_id)
        interview_service.start_analysis_and_questions(request.session_id)
        return {"message": "Analysis completed, gap analysis performed, and questions generated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-questions", response_model=Dict[str, str])
async def generate_questions(
    request: SessionRequest,
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Explicitly regenerate interview questions for the session (running up to question generation)."""
    try:
        interview_service.start_analysis_and_questions(request.session_id)
        return {"message": "Questions generated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mock-interview/start", response_model=Dict[str, Any])
async def start_mock_interview(
    request: SessionRequest,
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Start the mock interview conversation, presenting the first question."""
    try:
        # Retrieve next question details
        result = interview_service.get_next_question(request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mock-interview/answer", response_model=Dict[str, Any])
async def submit_mock_interview_answer(
    request: AnswerRequest,
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Submit the answer for the current question and immediately retrieve the next question/statement."""
    try:
        # 1. Submit current answer
        interview_service.submit_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            answer_text=request.answer_text
        )
        # 2. Get next question response
        result = interview_service.get_next_question(request.session_id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate", response_model=Dict[str, str])
async def evaluate_interview(
    request: SessionRequest,
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Finalize the mock interview, invoking the Evaluation and Career Coach Agents to generate reports."""
    try:
        interview_service.evaluate_session_and_recommend(request.session_id)
        return {"message": "Interview evaluated and career recommendations compiled successfully."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report", response_model=Dict[str, Any])
async def get_preparation_report(
    session_id: str,
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Fetch the complete generated report, including gap analysis, question history, evaluation, and coaching advice."""
    try:
        report = interview_service.get_full_report(session_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
