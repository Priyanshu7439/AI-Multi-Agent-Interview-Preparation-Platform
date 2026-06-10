from abc import ABC, abstractmethod
from typing import Optional, Tuple
from app.domain.schemas import (
    InterviewSession, 
    CandidateProfile, 
    JobRequirement, 
    SkillGap, 
    EvaluationResult, 
    CareerAdvice
)

class ISessionRepository(ABC):
    @abstractmethod
    def create_session(self, session_id: str) -> None:
        """Create a new interview preparation session."""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Retrieve the interview session state."""
        pass

    @abstractmethod
    def update_session(self, session: InterviewSession) -> None:
        """Update/persist the interview session state."""
        pass

    @abstractmethod
    def save_profile(self, session_id: str, profile: CandidateProfile) -> None:
        """Save candidate profile for the session."""
        pass

    @abstractmethod
    def get_profile(self, session_id: str) -> Optional[CandidateProfile]:
        """Retrieve candidate profile for the session."""
        pass

    @abstractmethod
    def save_job_requirement(self, session_id: str, requirement: JobRequirement) -> None:
        """Save job requirements for the session."""
        pass

    @abstractmethod
    def get_job_requirement(self, session_id: str) -> Optional[JobRequirement]:
        """Retrieve job requirements for the session."""
        pass

    @abstractmethod
    def save_skill_gap(self, session_id: str, gap: SkillGap) -> None:
        """Save skill gap analysis for the session."""
        pass

    @abstractmethod
    def get_skill_gap(self, session_id: str) -> Optional[SkillGap]:
        """Retrieve skill gap analysis for the session."""
        pass

    @abstractmethod
    def save_evaluation(self, session_id: str, evaluation: EvaluationResult) -> None:
        """Save mock interview evaluation for the session."""
        pass

    @abstractmethod
    def get_evaluation(self, session_id: str) -> Optional[EvaluationResult]:
        """Retrieve mock interview evaluation for the session."""
        pass

    @abstractmethod
    def save_career_advice(self, session_id: str, advice: CareerAdvice) -> None:
        """Save career advice and recommendations."""
        pass

    @abstractmethod
    def get_career_advice(self, session_id: str) -> Optional[CareerAdvice]:
        """Retrieve career advice and recommendations."""
        pass

    @abstractmethod
    def save_raw_texts(
        self, 
        session_id: str, 
        resume_text: Optional[str] = None, 
        jd_text: Optional[str] = None
    ) -> None:
        """Save raw parsed text inputs."""
        pass

    @abstractmethod
    def get_raw_texts(self, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Retrieve raw parsed text inputs (resume_text, jd_text)."""
        pass
