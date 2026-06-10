from app.graph.state import InterviewGraphState
from app.agents import (
    ResumeAnalyzerAgent,
    JDAnalyzerAgent,
    SkillGapAgent,
    InterviewQuestionGeneratorAgent,
    MockInterviewAgent,
    EvaluationAgent,
    CareerCoachAgent
)
from app.domain.interfaces import ISessionRepository
from app.core.logging import logger

class WorkflowNodes:
    def __init__(
        self,
        resume_agent: ResumeAnalyzerAgent,
        jd_agent: JDAnalyzerAgent,
        gap_agent: SkillGapAgent,
        question_agent: InterviewQuestionGeneratorAgent,
        interview_agent: MockInterviewAgent,
        evaluation_agent: EvaluationAgent,
        career_agent: CareerCoachAgent,
        repository: ISessionRepository
    ):
        self.resume_agent = resume_agent
        self.jd_agent = jd_agent
        self.gap_agent = gap_agent
        self.question_agent = question_agent
        self.interview_agent = interview_agent
        self.evaluation_agent = evaluation_agent
        self.career_agent = career_agent
        self.repository = repository

    def resume_analysis_node(self, state: InterviewGraphState) -> InterviewGraphState:
        logger.info("Nodes: Entering resume_analysis_node", session_id=state["session_id"])
        profile = state.get("candidate_profile") or self.repository.get_profile(state["session_id"])
        if not profile:
            profile = self.resume_agent.analyze(state["resume_text"])
            self.repository.save_profile(state["session_id"], profile)
        return {
            **state,
            "candidate_profile": profile,
            "current_node": "resume_analysis"
        }

    def jd_analysis_node(self, state: InterviewGraphState) -> InterviewGraphState:
        logger.info("Nodes: Entering jd_analysis_node", session_id=state["session_id"])
        requirement = state.get("job_requirements") or self.repository.get_job_requirement(state["session_id"])
        if not requirement:
            requirement = self.jd_agent.analyze(state["jd_text"])
            self.repository.save_job_requirement(state["session_id"], requirement)
        return {
            **state,
            "job_requirements": requirement,
            "current_node": "jd_analysis"
        }

    def gap_analysis_node(self, state: InterviewGraphState) -> InterviewGraphState:
        logger.info("Nodes: Entering gap_analysis_node", session_id=state["session_id"])
        profile = state.get("candidate_profile") or self.repository.get_profile(state["session_id"])
        requirement = state.get("job_requirements") or self.repository.get_job_requirement(state["session_id"])
        
        if not profile or not requirement:
            logger.error("Missing candidate profile or job requirements for gap analysis")
            raise ValueError("Candidate profile and job requirements are required for skill gap analysis")

        gap = state.get("skill_gap") or self.repository.get_skill_gap(state["session_id"])
        if not gap:
            gap = self.gap_agent.analyze(profile, requirement)
            self.repository.save_skill_gap(state["session_id"], gap)
        return {
            **state,
            "skill_gap": gap,
            "current_node": "gap_analysis"
        }

    def question_generation_node(self, state: InterviewGraphState) -> InterviewGraphState:
        logger.info("Nodes: Entering question_generation_node", session_id=state["session_id"])
        profile = state.get("candidate_profile") or self.repository.get_profile(state["session_id"])
        requirement = state.get("job_requirements") or self.repository.get_job_requirement(state["session_id"])
        skill_gap = state.get("skill_gap") or self.repository.get_skill_gap(state["session_id"])

        if not profile or not requirement or not skill_gap:
            raise ValueError("Required data missing for question generation")

        db_session = self.repository.get_session(state["session_id"])
        questions = []
        if db_session and db_session.questions:
            questions = db_session.questions
        else:
            questions = self.question_agent.generate_questions(
                session_id=state["session_id"],
                profile=profile,
                requirement=requirement,
                skill_gap=skill_gap
            )
            if db_session:
                db_session.questions = questions
                db_session.status = "ongoing"
                self.repository.update_session(db_session)

        return {
            **state,
            "questions": questions,
            "current_node": "question_generation"
        }

    def mock_interview_node(self, state: InterviewGraphState) -> InterviewGraphState:
        logger.info("Nodes: Entering mock_interview_node", session_id=state["session_id"])
        
        # Load current session details
        db_session = self.repository.get_session(state["session_id"])
        if not db_session:
            raise ValueError(f"Session {state['session_id']} not found in repository")

        # Sync state with DB session state
        questions = db_session.questions
        answers = db_session.answers
        current_idx = db_session.current_question_index

        logger.info(
            "Mock Interview Node Status", 
            questions_count=len(questions), 
            answers_count=len(answers), 
            current_index=current_idx
        )

        return {
            **state,
            "questions": questions,
            "answers": answers,
            "current_node": "mock_interview"
        }

    def evaluation_node(self, state: InterviewGraphState) -> InterviewGraphState:
        logger.info("Nodes: Entering evaluation_node", session_id=state["session_id"])
        db_session = self.repository.get_session(state["session_id"])
        if not db_session:
            raise ValueError(f"Session {state['session_id']} not found")

        questions = db_session.questions
        answers = db_session.answers

        if not answers:
            logger.warning("No answers submitted. Creating an empty evaluation.")
            evaluation = EvaluationResult(scores={"overall": 0.0}, weaknesses=["Candidate did not answer any questions."], strengths=[], feedback=[])
        else:
            evaluation = self.evaluation_agent.evaluate(
                session_id=state["session_id"],
                questions=questions,
                answers=answers
            )

        self.repository.save_evaluation(state["session_id"], evaluation)
        return {
            **state,
            "evaluation": evaluation,
            "current_node": "evaluation"
        }

    def career_coaching_node(self, state: InterviewGraphState) -> InterviewGraphState:
        logger.info("Nodes: Entering career_coaching_node", session_id=state["session_id"])
        
        profile = state.get("candidate_profile") or self.repository.get_profile(state["session_id"])
        requirement = state.get("job_requirements") or self.repository.get_job_requirement(state["session_id"])
        skill_gap = state.get("skill_gap") or self.repository.get_skill_gap(state["session_id"])
        evaluation = state.get("evaluation") or self.repository.get_evaluation(state["session_id"])

        if not profile or not requirement or not skill_gap or not evaluation:
            raise ValueError("Required data missing for career coaching")

        advice = self.career_agent.generate_advice(
            session_id=state["session_id"],
            profile=profile,
            requirement=requirement,
            skill_gap=skill_gap,
            evaluation=evaluation
        )

        self.repository.save_career_advice(state["session_id"], advice)
        
        # Complete session in database
        db_session = self.repository.get_session(state["session_id"])
        if db_session:
            db_session.status = "completed"
            self.repository.update_session(db_session)

        return {
            **state,
            "career_advice": advice,
            "current_node": "career_coaching"
        }
