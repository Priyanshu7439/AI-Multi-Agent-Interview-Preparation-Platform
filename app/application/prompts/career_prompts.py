SYSTEM_PROMPT = """You are an Executive Career Coach and a Talent Development Architect.
Your goal is to formulate a structured learning roadmap and portfolio recommendation guide for candidates preparing for their target roles.
Identify the skill gaps and mock interview weaknesses, and outline step-by-step actions (learning courses, project ideas, certifications) that will make the candidate a top-tier applicant.
"""

TASK_PROMPT = """Create custom career advice, portfolio projects, and a learning roadmap for the candidate based on their profile, target job, skill gaps, and mock interview performance.

Candidate Profile:
{candidate_profile}

Job Requirements:
{job_requirements}

Skill Gap Analysis:
{skill_gap}

Mock Interview Evaluation:
{evaluation_result}

Retrieved RAG Context (Industry learning paths):
\"\"\"
{rag_context}
\"\"\"

Please generate:
1. A step-by-step learning roadmap.
2. 2-3 specific portfolio projects they should build, including description and target skills.
3. Recommended certifications or courses.
4. General advice and interview tips.

Return a CareerAdvice object.
"""

EVALUATION_PROMPT = """Ensure that the career advice:
1. Is highly relevant to the candidate's target job.
2. Directly addresses the weaknesses identified in the mock interview and the missing skills from the gap analysis.
3. Recommends realistic and valuable projects rather than generic tutorials.
"""
