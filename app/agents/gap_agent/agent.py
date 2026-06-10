from app.domain.interfaces.llm_service import ILLMService
from app.domain.schemas.profile import CandidateProfile
from app.domain.schemas.requirements import JobRequirement
from app.domain.schemas.gap import SkillGap
from app.application.prompts.gap_prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.core.logging import logger

class SkillGapAgent:
    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service

    def analyze(self, profile: CandidateProfile, requirement: JobRequirement) -> SkillGap:
        logger.info("SkillGapAgent: Starting skill gap analysis")
        prompt = TASK_PROMPT.format(
            candidate_profile=profile.model_dump_json(indent=2),
            job_requirements=requirement.model_dump_json(indent=2)
        )
        gap = self.llm_service.generate_structured_output(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=SkillGap
        )
        logger.info("SkillGapAgent: Gap analysis completed", match_percentage=gap.match_percentage)
        return gap
