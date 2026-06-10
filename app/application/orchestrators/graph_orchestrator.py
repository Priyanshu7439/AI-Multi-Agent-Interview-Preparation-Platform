from app.graph.workflow import create_interview_workflow
from app.graph.nodes import WorkflowNodes
from app.graph.state import InterviewGraphState
from app.domain.interfaces import ISessionRepository
from app.core.logging import logger

class GraphOrchestrator:
    def __init__(self, workflow_nodes: WorkflowNodes):
        self.graph = create_interview_workflow(workflow_nodes)
        self.repository = workflow_nodes.repository

    def run_analysis_and_prep(self, session_id: str) -> None:
        """Run the graph up to the mock interview page. Generates profile, requirements, gaps, and questions."""
        logger.info("GraphOrchestrator: Starting analysis and question generation flow", session_id=session_id)
        
        resume_text, jd_text = self.repository.get_raw_texts(session_id)
        if not resume_text or not jd_text:
            raise ValueError(f"Missing resume_text or jd_text for session {session_id}")

        # Construct initial graph state
        initial_state: InterviewGraphState = {
            "session_id": session_id,
            "resume_text": resume_text,
            "jd_text": jd_text,
            "candidate_profile": None,
            "job_requirements": None,
            "skill_gap": None,
            "questions": [],
            "answers": [],
            "evaluation": None,
            "career_advice": None,
            "current_node": ""
        }

        # Run state graph (compiled workflow)
        final_state = self.graph.invoke(initial_state)
        logger.info("GraphOrchestrator: Prep phase completed", session_id=session_id, stopped_at_node=final_state.get("current_node"))

    def run_evaluation_and_coach(self, session_id: str) -> None:
        """Run the evaluation and career coaching nodes of the graph."""
        logger.info("GraphOrchestrator: Starting evaluation and coaching flow", session_id=session_id)

        # Load existing details from SQL database to build state
        db_session = self.repository.get_session(session_id)
        if not db_session:
            raise ValueError(f"Session {session_id} not found in database")

        resume_text, jd_text = self.repository.get_raw_texts(session_id)
        profile = self.repository.get_profile(session_id)
        requirement = self.repository.get_job_requirement(session_id)
        skill_gap = self.repository.get_skill_gap(session_id)

        # Build full state for the workflow run
        state: InterviewGraphState = {
            "session_id": session_id,
            "resume_text": resume_text or "",
            "jd_text": jd_text or "",
            "candidate_profile": profile,
            "job_requirements": requirement,
            "skill_gap": skill_gap,
            "questions": db_session.questions,
            "answers": db_session.answers,
            "evaluation": None,
            "career_advice": None,
            "current_node": "mock_interview"
        }

        # Execute the graph. Because profile/gaps are present,
        # they will be skipped, routing directly through mock_interview to evaluation and career coaching
        final_state = self.graph.invoke(state)
        logger.info("GraphOrchestrator: Evaluation and coaching completed successfully", session_id=session_id)
