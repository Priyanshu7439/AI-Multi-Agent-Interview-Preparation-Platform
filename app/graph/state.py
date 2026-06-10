from typing import TypedDict, Optional, List
from app.domain.schemas import (
    CandidateProfile,
    JobRequirement,
    SkillGap,
    InterviewQuestion,
    CandidateAnswer,
    EvaluationResult,
    CareerAdvice
)

class InterviewGraphState(TypedDict):
    session_id: str
    resume_text: str
    jd_text: str
    candidate_profile: Optional[CandidateProfile]
    job_requirements: Optional[JobRequirement]
    skill_gap: Optional[SkillGap]
    questions: List[InterviewQuestion]
    answers: List[CandidateAnswer]
    evaluation: Optional[EvaluationResult]
    career_advice: Optional[CareerAdvice]
    current_node: str
