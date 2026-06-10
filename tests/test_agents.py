import pytest
from app.agents import (
    ResumeAnalyzerAgent,
    JDAnalyzerAgent,
    SkillGapAgent,
    InterviewQuestionGeneratorAgent,
    MockInterviewAgent,
    EvaluationAgent,
    CareerCoachAgent
)
from app.domain.schemas import (
    CandidateProfile,
    JobRequirement,
    SkillGap,
    InterviewQuestion,
    InterviewSession,
    CandidateAnswer,
    EvaluationResult,
    CareerAdvice
)

def test_resume_analyzer_agent(mock_llm):
    agent = ResumeAnalyzerAgent(mock_llm)
    profile = agent.analyze("Raw resume text contents")
    assert profile.full_name == "Alice Smith"
    assert "FastAPI" in profile.skills

def test_jd_analyzer_agent(mock_llm):
    agent = JDAnalyzerAgent(mock_llm)
    req = agent.analyze("Raw JD text contents")
    assert req.title == "Senior Backend Engineer"
    assert "Python" in req.required_skills

def test_skill_gap_agent(mock_llm):
    agent = SkillGapAgent(mock_llm)
    profile = CandidateProfile(full_name="Test", skills=["Python"])
    requirement = JobRequirement(title="Engineer", required_skills=["Python", "PostgreSQL"])
    gap = agent.analyze(profile, requirement)
    assert gap.match_percentage == 75.0
    assert "PostgreSQL" in gap.missing_skills

def test_question_generator_agent(mock_llm, mock_vector_store):
    agent = InterviewQuestionGeneratorAgent(mock_llm, mock_vector_store)
    profile = CandidateProfile(full_name="Test", skills=["Python"])
    requirement = JobRequirement(title="Engineer", required_skills=["Python", "PostgreSQL"])
    gap = SkillGap(match_percentage=50.0, missing_skills=["PostgreSQL"])
    questions = agent.generate_questions("sess1", profile, requirement, gap)
    assert len(questions) == 2
    assert questions[0].id == "q1"

def test_mock_interview_agent(mock_llm):
    agent = MockInterviewAgent(mock_llm)
    session = InterviewSession(
        session_id="sess1",
        questions=[InterviewQuestion(id="q1", question_text="What is FastAPI?", category="tech", difficulty="easy", expected_points=[])]
    )
    prompt = agent.generate_next_response(session)
    assert "Mocked interviewer statement" in prompt

def test_evaluation_agent(mock_llm, mock_vector_store):
    agent = EvaluationAgent(mock_llm, mock_vector_store)
    questions = [InterviewQuestion(id="q1", question_text="What is FastAPI?", category="tech", difficulty="easy", expected_points=[])]
    answers = [CandidateAnswer(question_id="q1", answer_text="It is a web framework.")]
    evaluation = agent.evaluate("sess1", questions, answers)
    assert evaluation.scores["overall"] == 8.5
    assert len(evaluation.feedback) == 1

def test_career_coach_agent(mock_llm, mock_vector_store):
    agent = CareerCoachAgent(mock_llm, mock_vector_store)
    profile = CandidateProfile(full_name="Test", skills=["Python"])
    requirement = JobRequirement(title="Engineer", required_skills=["Python"])
    gap = SkillGap(match_percentage=100.0)
    evaluation = EvaluationResult(scores={"overall": 8.0})
    advice = agent.generate_advice("sess1", profile, requirement, gap, evaluation)
    assert len(advice.roadmap) == 2
    assert advice.recommended_projects[0].name == "E-Commerce API with PostgreSQL"
