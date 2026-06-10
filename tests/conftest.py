import pytest
from typing import Type, TypeVar, List
from app.domain.interfaces import ILLMService, IVectorStoreService, ISessionRepository
from app.domain.schemas import (
    CandidateProfile,
    JobRequirement,
    SkillGap,
    InterviewQuestion,
    InterviewSession,
    EvaluationResult,
    CareerAdvice,
    RecommendedProject,
    QuestionFeedback,
    CandidateAnswer
)

T = TypeVar("T")

class MockLLMService(ILLMService):
    def generate_structured_output(
        self, 
        prompt: str, 
        system_prompt: str, 
        response_model: Type[T]
    ) -> T:
        if response_model.__name__ == "CandidateProfile":
            return CandidateProfile(
                full_name="Alice Smith",
                email="alice@example.com",
                phone="555-0199",
                skills=["Python", "FastAPI", "Docker"],
                experience=[],
                projects=[],
                education=[]
            )
        elif response_model.__name__ == "JobRequirement":
            return JobRequirement(
                title="Senior Backend Engineer",
                required_skills=["Python", "FastAPI", "PostgreSQL"],
                preferred_skills=["Docker", "Kubernetes"],
                responsibilities=["Design APIs", "Maintain infrastructure"],
                qualifications=["BS in Computer Science"],
                keywords=["Backend", "FastAPI"]
            )
        elif response_model.__name__ == "SkillGap":
            return SkillGap(
                missing_skills=["PostgreSQL"],
                matching_skills=["Python", "FastAPI", "Docker"],
                match_percentage=75.0,
                improvement_suggestions=["Learn PostgreSQL schemas and SQL queries."]
            )
        elif response_model.__name__ == "QuestionsList":
            from app.agents.question_agent.agent import QuestionsList
            return QuestionsList(
                questions=[
                    InterviewQuestion(
                        id="q1",
                        question_text="How do you handle dependency injection in FastAPI?",
                        category="technical",
                        difficulty="intermediate",
                        expected_points=["Depends", "di", "testing overrides"]
                    ),
                    InterviewQuestion(
                        id="q2",
                        question_text="Tell me about a time you resolved a major bug in production.",
                        category="behavioral",
                        difficulty="intermediate",
                        expected_points=["STAR", "incident resolution", "post-mortem"]
                    )
                ]
            )
        elif response_model.__name__ == "EvaluationResult":
            return EvaluationResult(
                scores={"q1": 8.0, "q2": 9.0, "overall": 8.5},
                weaknesses=["Needs to specify async/await optimizations in FastAPI"],
                strengths=["Great STAR method application"],
                feedback=[
                    QuestionFeedback(
                        question_id="q1",
                        score=8.0,
                        explanation="Good answer, but missed async details.",
                        sample_good_answer="Use Depends with async def functions..."
                    )
                ]
            )
        elif response_model.__name__ == "CareerAdvice":
            return CareerAdvice(
                roadmap=["1. Learn SQL", "2. Build PostgreSQL projects"],
                recommended_projects=[
                    RecommendedProject(
                        name="E-Commerce API with PostgreSQL",
                        description="Build a FastAPI system with relational DB",
                        target_skills=["PostgreSQL", "SQLAlchemy"]
                    )
                ],
                recommended_certifications=["Google Professional Cloud Architect"],
                general_tips=["Practice coding puzzles", "Be concise in behavioral answers"]
            )
        
        # Default fallback instantiation
        return response_model()

    def generate_text(self, prompt: str, system_prompt: str) -> str:
        return "Mocked interviewer statement asking the next question."

class MockVectorStoreService(IVectorStoreService):
    def add_documents(self, collection_name: str, texts: List[str], metadatas: List[dict], ids: List[str]) -> None:
        pass
    def similarity_search(self, collection_name: str, query: str, k: int = 4) -> List[str]:
        return ["Mock RAG Document Chunk 1", "Mock RAG Document Chunk 2"]
    def clear_collection(self, collection_name: str) -> None:
        pass

@pytest.fixture
def mock_llm() -> ILLMService:
    return MockLLMService()

@pytest.fixture
def mock_vector_store() -> IVectorStoreService:
    return MockVectorStoreService()
