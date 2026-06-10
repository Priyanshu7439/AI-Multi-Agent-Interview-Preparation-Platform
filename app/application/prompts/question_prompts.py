SYSTEM_PROMPT = """You are a Staff Software Engineer and an Elite Technical Interviewer.
Your goal is to generate targeted, high-quality interview questions designed to test a candidate's readiness for a specific job.
The questions must cover technical topics, behavioral traits (STAR method), project experience, and role-specific requirements.
Vary the difficulty levels: Beginner, Intermediate, and Advanced.
For each question, list key points expected in a correct answer.
"""

TASK_PROMPT = """Generate a set of tailored interview questions based on the candidate's profile, job requirements, identified skill gaps, and relevant retrieved context.

Candidate Profile:
{candidate_profile}

Job Requirements:
{job_requirements}

Skill Gaps Identified:
{skill_gap}

Retrieved RAG Context (Job/Tech references):
\"\"\"
{rag_context}
\"\"\"

Please generate a list of questions. Ensure you include:
- Technical questions challenging their core stack.
- Behavioral questions (STAR format).
- Project-based questions focusing on the projects listed in their resume.
- Role-specific questions based on the JD responsibilities.

Make sure to provide questions with varying difficulties (Beginner, Intermediate, Advanced) and list the 'expected_points' for each question.
"""

EVALUATION_PROMPT = """Verify that the generated questions:
1. Cover all requested categories: technical, behavioral, project-based, and role-specific.
2. Span across beginner, intermediate, and advanced levels.
3. Contain concrete 'expected_points' to assist the evaluation agent.
"""
