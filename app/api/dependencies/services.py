from app.core.config import settings
from app.infrastructure.parsers.pdf_parser import PDFParserService
from app.infrastructure.llm.gemini_client import GeminiLLMService
from app.infrastructure.vectorstore.chroma_client import ChromaStoreService
from app.infrastructure.repositories.sqlite_repository import SQLiteSessionRepository
from app.agents import (
    ResumeAnalyzerAgent,
    JDAnalyzerAgent,
    SkillGapAgent,
    InterviewQuestionGeneratorAgent,
    MockInterviewAgent,
    EvaluationAgent,
    CareerCoachAgent
)
from app.graph.nodes import WorkflowNodes
from app.application.orchestrators.graph_orchestrator import GraphOrchestrator
from app.application.services import ResumeService, JobService, InterviewService

# 1. Initialize Singletons of Infrastructure
_parser_service = PDFParserService()
_llm_service = GeminiLLMService()
_vector_store = ChromaStoreService(settings.CHROMA_DB_PATH)
_repository = SQLiteSessionRepository(settings.DATABASE_URL)

# 2. Initialize Singletons of Agents
_resume_agent = ResumeAnalyzerAgent(_llm_service)
_jd_agent = JDAnalyzerAgent(_llm_service)
_gap_agent = SkillGapAgent(_llm_service)
_question_agent = InterviewQuestionGeneratorAgent(_llm_service, _vector_store)
_interview_agent = MockInterviewAgent(_llm_service)
_evaluation_agent = EvaluationAgent(_llm_service, _vector_store)
_career_agent = CareerCoachAgent(_llm_service, _vector_store)

# 3. Initialize Workflow Nodes & Orchestrator
_workflow_nodes = WorkflowNodes(
    resume_agent=_resume_agent,
    jd_agent=_jd_agent,
    gap_agent=_gap_agent,
    question_agent=_question_agent,
    interview_agent=_interview_agent,
    evaluation_agent=_evaluation_agent,
    career_agent=_career_agent,
    repository=_repository
)
_orchestrator = GraphOrchestrator(_workflow_nodes)

# 4. Initialize Application Services
_resume_service = ResumeService(_parser_service, _repository, _vector_store)
_job_service = JobService(_parser_service, _repository, _vector_store)
_interview_service = InterviewService(_repository, _interview_agent, _orchestrator)

# 5. DI Getter Functions
def get_resume_service() -> ResumeService:
    return _resume_service

def get_job_service() -> JobService:
    return _job_service

def get_interview_service() -> InterviewService:
    return _interview_service
