from app.domain.interfaces.llm_service import ILLMService
from app.domain.schemas.profile import CandidateProfile
from app.application.prompts.resume_prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.core.logging import logger

class ResumeAnalyzerAgent:
    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service

    def analyze(self, resume_text: str) -> CandidateProfile:
        logger.info("ResumeAnalyzerAgent: Starting resume analysis")
        prompt = TASK_PROMPT.format(resume_text=resume_text)
        profile = self.llm_service.generate_structured_output(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=CandidateProfile
        )
        logger.info("ResumeAnalyzerAgent: Resume analyzed successfully", candidate_name=profile.full_name)
        return profile
