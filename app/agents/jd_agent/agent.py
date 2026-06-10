from app.domain.interfaces.llm_service import ILLMService
from app.domain.schemas.requirements import JobRequirement
from app.application.prompts.jd_prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.core.logging import logger

class JDAnalyzerAgent:
    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service

    def analyze(self, jd_text: str) -> JobRequirement:
        logger.info("JDAnalyzerAgent: Starting job description analysis")
        prompt = TASK_PROMPT.format(jd_text=jd_text)
        requirement = self.llm_service.generate_structured_output(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=JobRequirement
        )
        logger.info("JDAnalyzerAgent: Job description analyzed successfully", job_title=requirement.title)
        return requirement
