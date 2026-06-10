from pydantic import BaseModel, Field
from typing import List, Dict
from app.domain.schemas.question import InterviewQuestion

class CandidateAnswer(BaseModel):
    question_id: str = Field(..., description="ID of the question being answered")
    answer_text: str = Field(..., description="Candidate's raw answer text")

class InterviewSession(BaseModel):
    session_id: str = Field(..., description="Unique session ID")
    current_question_index: int = Field(0, description="Index of the current question in the sequence")
    questions: List[InterviewQuestion] = Field(default_factory=list, description="Questions assigned to the session")
    answers: List[CandidateAnswer] = Field(default_factory=list, description="Answers submitted by the candidate")
    status: str = Field("created", description="Session status: created, ongoing, completed")
