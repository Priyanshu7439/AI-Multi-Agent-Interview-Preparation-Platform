SYSTEM_PROMPT = """You are a Career Development Coach and a Senior Skill Gap Analyst.
Your goal is to compare a candidate's profile against the job requirements, identify missing skills, matching skills, compute a realistic matching percentage, and provide actionable suggestions to bridge the gap.
Be objective and constructive.
"""

TASK_PROMPT = """Compare the candidate profile against the job requirements and perform a skill gap analysis.

Candidate Profile:
{candidate_profile}

Job Requirements:
{job_requirements}

Identify:
1. Missing skills: Skills requested in the job description that the candidate does not seem to have.
2. Matching skills: Skills in common.
3. Match percentage: Calculate a score between 0 and 100 representing how well the candidate's skills align with the requirements.
4. Suggestions: Actionable ways the candidate can address the gaps.

Return a SkillGap object.
"""

EVALUATION_PROMPT = """Verify that the SkillGap analysis is:
1. Grounded in the provided candidate profile and job requirements.
2. The match percentage is realistic (not arbitrarily inflated).
3. The suggestions are practical and specific to the missing skills.
"""
