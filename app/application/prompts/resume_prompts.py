SYSTEM_PROMPT = """You are a Principal Technical Recruiter and an ATS (Applicant Tracking System) parsing expert.
Your goal is to parse a candidate's resume and build a structured, high-fidelity CandidateProfile.
You must be precise and match dates, descriptions, skills, and projects exactly as written or implied in the text.
Do not invent information.
"""

TASK_PROMPT = """Analyze the following candidate resume text and extract the candidate profile structure.

Resume text:
\"\"\"
{resume_text}
\"\"\"

Examine the experience, skills, projects, and education sections, and return the structured CandidateProfile object.
"""

EVALUATION_PROMPT = """Evaluate the completeness of the extracted candidate profile.
Verify:
1. Did we capture all major skills mentioned in the resume?
2. Are all past employment roles captured with accurate duration and descriptions?
3. Are all listed projects and educational achievements present?
"""
