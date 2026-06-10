from app.domain.interfaces.llm_service import ILLMService
from app.domain.interfaces.vector_store import IVectorStoreService
from app.domain.schemas import CandidateProfile, JobRequirement, SkillGap, EvaluationResult, CareerAdvice
from app.application.prompts.career_prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.core.logging import logger

class CareerCoachAgent:
    def __init__(self, llm_service: ILLMService, vector_store: IVectorStoreService = None):
        self.llm_service = llm_service
        self.vector_store = vector_store

    def generate_advice(
        self, 
        session_id: str, 
        profile: CandidateProfile, 
        requirement: JobRequirement, 
        skill_gap: SkillGap, 
        evaluation: EvaluationResult
    ) -> CareerAdvice:
        """Formulate custom career advice, roadmap, and projects based on candidate performance and JD gaps."""
        logger.info("CareerCoachAgent: Starting advice generation")

        # 1. RAG Context Retrieval
        rag_context = ""
        if self.vector_store:
            try:
                # Query vector store focusing on missing skills and role training
                query = f"Target Role: {requirement.title}. Critical skills: {', '.join(skill_gap.missing_skills or requirement.required_skills[:3])}"
                chunks = self.vector_store.similarity_search(
                    collection_name=f"jd_{session_id}",
                    query=query,
                    k=3
                )
                if chunks:
                    rag_context = "\n\n".join(chunks)
                    logger.info("CareerCoachAgent: RAG context retrieved successfully", chunk_count=len(chunks))
            except Exception as e:
                logger.warning("CareerCoachAgent: RAG retrieval failed, proceeding without context", error=str(e))

        # 2. Invoke LLM with prompts
        prompt = TASK_PROMPT.format(
            candidate_profile=profile.model_dump_json(indent=2),
            job_requirements=requirement.model_dump_json(indent=2),
            skill_gap=skill_gap.model_dump_json(indent=2),
            evaluation_result=evaluation.model_dump_json(indent=2),
            rag_context=rag_context or "No additional context retrieved."
        )

        advice = self.llm_service.generate_structured_output(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=CareerAdvice
        )

        logger.info("CareerCoachAgent: Career advice generated successfully")
        return advice
