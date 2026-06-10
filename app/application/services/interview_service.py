from typing import Optional, Dict, Any, Tuple
from app.domain.interfaces import ISessionRepository
from app.domain.schemas import InterviewSession, CandidateAnswer
from app.agents.interview_agent.agent import MockInterviewAgent
from app.application.orchestrators.graph_orchestrator import GraphOrchestrator
from app.core.exceptions import SessionNotFoundException, InvalidStateException
from app.core.logging import logger

class InterviewService:
    def __init__(
        self,
        repository: ISessionRepository,
        interview_agent: MockInterviewAgent,
        orchestrator: GraphOrchestrator
    ):
        self.repository = repository
        self.interview_agent = interview_agent
        self.orchestrator = orchestrator

    def create_session(self, session_id: str) -> None:
        """Create a new session record in the repository."""
        self.repository.create_session(session_id)

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Retrieve interview session state."""
        return self.repository.get_session(session_id)

    def start_analysis_and_questions(self, session_id: str) -> None:
        """Trigger the analysis and question generation phases in the LangGraph workflow."""
        db_session = self.repository.get_session(session_id)
        if not db_session:
            raise SessionNotFoundException(f"Session {session_id} not found")
        
        self.orchestrator.run_analysis_and_prep(session_id)

    def get_next_question(self, session_id: str) -> Dict[str, Any]:
        """Acknowledge the candidate's last answer and present the next question conversationally."""
        session = self.repository.get_session(session_id)
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found")

        if session.status == "created":
            raise InvalidStateException("Session is not analyzed yet. Generate questions first.")

        if session.current_question_index >= len(session.questions):
            return {
                "interviewer_prompt": "The mock interview is now complete! Thank you for your time. Please click Evaluate to view your results.",
                "question": None,
                "current_question_index": session.current_question_index,
                "total_questions": len(session.questions),
                "is_complete": True
            }

        # Use MockInterviewAgent to formulate conversational prompt
        interviewer_prompt = self.interview_agent.generate_next_response(session)
        current_question = session.questions[session.current_question_index]

        return {
            "interviewer_prompt": interviewer_prompt,
            "question": current_question,
            "current_question_index": session.current_question_index + 1,
            "total_questions": len(session.questions),
            "is_complete": False
        }

    def submit_answer(self, session_id: str, question_id: str, answer_text: str) -> None:
        """Submit candidate answer for the current question and increment current question index."""
        session = self.repository.get_session(session_id)
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found")

        if session.status == "completed":
            raise InvalidStateException("Cannot submit answer to a completed interview")

        # Validate that the candidate is answering the correct current question
        if session.current_question_index >= len(session.questions):
            raise InvalidStateException("All questions have already been answered")

        current_q = session.questions[session.current_question_index]
        if current_q.id != question_id:
            raise InvalidStateException(f"Mismatch: expected answer for question {current_q.id}, got answer for {question_id}")

        # Record candidate answer
        candidate_answer = CandidateAnswer(question_id=question_id, answer_text=answer_text)
        session.answers.append(candidate_answer)
        
        # Advance index
        session.current_question_index += 1
        
        # Update in database
        self.repository.update_session(session)
        logger.info(
            "Submitted candidate answer", 
            session_id=session_id, 
            question_id=question_id, 
            next_index=session.current_question_index
        )

    def evaluate_session_and_recommend(self, session_id: str) -> None:
        """Trigger mock interview evaluation and career coaching phases in the LangGraph workflow."""
        session = self.repository.get_session(session_id)
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found")

        if session.current_question_index < len(session.questions):
            raise InvalidStateException(
                f"Cannot evaluate session: only {session.current_question_index}/{len(session.questions)} questions answered"
            )

        self.orchestrator.run_evaluation_and_coach(session_id)

    def get_full_report(self, session_id: str) -> Dict[str, Any]:
        """Gather all outputs for the session and compile a final, comprehensive report."""
        session = self.repository.get_session(session_id)
        if not session:
            raise SessionNotFoundException(f"Session {session_id} not found")

        profile = self.repository.get_profile(session_id)
        requirement = self.repository.get_job_requirement(session_id)
        skill_gap = self.repository.get_skill_gap(session_id)
        evaluation = self.repository.get_evaluation(session_id)
        career_advice = self.repository.get_career_advice(session_id)

        return {
            "session_id": session_id,
            "status": session.status,
            "candidate_profile": profile.model_dump() if profile else None,
            "job_requirements": requirement.model_dump() if requirement else None,
            "skill_gap": skill_gap.model_dump() if skill_gap else None,
            "evaluation": evaluation.model_dump() if evaluation else None,
            "career_advice": career_advice.model_dump() if career_advice else None
        }
