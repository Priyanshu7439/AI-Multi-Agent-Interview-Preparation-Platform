import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.services import get_resume_service, get_job_service, get_interview_service
from app.domain.schemas import InterviewQuestion, CandidateProfile, JobRequirement, SkillGap, EvaluationResult, CareerAdvice

# Create dummy mock service classes for API routes testing
class MockResumeService:
    def process_resume(self, session_id: str, file_bytes: bytes) -> str:
        return "Alice Smith resume text"

class MockJobService:
    def process_job_description(self, session_id: str, jd_text: str = None, file_bytes: bytes = None) -> str:
        return "Backend Engineer role description"

class MockInterviewService:
    def create_session(self, session_id: str) -> None:
        pass

    def start_analysis_and_questions(self, session_id: str) -> None:
        pass

    def get_next_question(self, session_id: str) -> dict:
        return {
            "interviewer_prompt": "First question: What is FastAPI?",
            "question": {
                "id": "q1",
                "question_text": "What is FastAPI?",
                "category": "technical",
                "difficulty": "beginner",
                "expected_points": ["Fast", "Pydantic"]
            },
            "current_question_index": 1,
            "total_questions": 5,
            "is_complete": False
        }

    def submit_answer(self, session_id: str, question_id: str, answer_text: str) -> None:
        pass

    def evaluate_session_and_recommend(self, session_id: str) -> None:
        pass

    def get_full_report(self, session_id: str) -> dict:
        return {
            "session_id": session_id,
            "status": "completed",
            "candidate_profile": {"full_name": "Alice Smith", "skills": ["Python"]},
            "job_requirements": {"title": "Backend Engineer", "required_skills": ["Python"]},
            "skill_gap": {"match_percentage": 100.0},
            "evaluation": {"scores": {"overall": 9.0}},
            "career_advice": {"roadmap": ["Learn SQL"]}
        }

@pytest.fixture(scope="module")
def client():
    # Set overrides
    app.dependency_overrides[get_resume_service] = lambda: MockResumeService()
    app.dependency_overrides[get_job_service] = lambda: MockJobService()
    app.dependency_overrides[get_interview_service] = lambda: MockInterviewService()
    
    with TestClient(app) as c:
        yield c
        
    # Clear overrides
    app.dependency_overrides.clear()

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_resume_upload(client):
    file_content = b"%PDF-1.4 Mock PDF content"
    response = client.post(
        "/resume/upload",
        files={"file": ("resume.pdf", file_content, "application/pdf")},
        data={"session_id": "test-sess-123"}
    )
    assert response.status_code == 200
    assert response.json()["session_id"] == "test-sess-123"

def test_job_upload_text(client):
    response = client.post(
        "/job/upload",
        data={"session_id": "test-sess-123", "jd_text": "Job details description text"}
    )
    assert response.status_code == 200
    assert response.json()["session_id"] == "test-sess-123"

def test_analyze(client):
    response = client.post("/analyze", json={"session_id": "test-sess-123"})
    assert response.status_code == 200
    assert "Analysis completed" in response.json()["message"]

def test_generate_questions(client):
    response = client.post("/generate-questions", json={"session_id": "test-sess-123"})
    assert response.status_code == 200
    assert "generated successfully" in response.json()["message"]

def test_mock_interview_start(client):
    response = client.post("/mock-interview/start", json={"session_id": "test-sess-123"})
    assert response.status_code == 200
    assert response.json()["current_question_index"] == 1
    assert response.json()["is_complete"] is False

def test_mock_interview_answer(client):
    response = client.post(
        "/mock-interview/answer",
        json={
            "session_id": "test-sess-123",
            "question_id": "q1",
            "answer_text": "FastAPI is a Python web framework built on Starlette and Pydantic."
        }
    )
    assert response.status_code == 200
    assert response.json()["current_question_index"] == 1

def test_evaluate(client):
    response = client.post("/evaluate", json={"session_id": "test-sess-123"})
    assert response.status_code == 200
    assert "Interview evaluated" in response.json()["message"]

def test_get_report(client):
    response = client.get("/report", params={"session_id": "test-sess-123"})
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-sess-123"
    assert data["candidate_profile"]["full_name"] == "Alice Smith"
