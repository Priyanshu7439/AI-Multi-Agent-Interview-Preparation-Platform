from typing import List
from pydantic import BaseModel, Field
from app.domain.interfaces.llm_service import ILLMService
from app.domain.interfaces.vector_store import IVectorStoreService
from app.domain.schemas import CandidateProfile, JobRequirement, SkillGap, InterviewQuestion
from app.application.prompts.question_prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.core.logging import logger

class QuestionsList(BaseModel):
    questions: List[InterviewQuestion] = Field(..., description="List of generated interview questions")

class InterviewQuestionGeneratorAgent:
    def __init__(self, llm_service: ILLMService, vector_store: IVectorStoreService = None):
        self.llm_service = llm_service
        self.vector_store = vector_store

    def generate_questions(
        self, 
        session_id: str, 
        profile: CandidateProfile, 
        requirement: JobRequirement, 
        skill_gap: SkillGap
    ) -> List[InterviewQuestion]:
        """Generate a structured list of interview questions using optional RAG context."""
        logger.info("QuestionGeneratorAgent: Starting question generation")
        
        # 1. RAG Context Retrieval
        rag_context = ""
        if self.vector_store:
            try:
                # Query vector store for the target job requirements context
                query = f"Job title: {requirement.title}. Key skills: {', '.join(requirement.required_skills)}"
                chunks = self.vector_store.similarity_search(
                    collection_name=f"jd_{session_id}",
                    query=query,
                    k=3
                )
                if chunks:
                    rag_context = "\n\n".join(chunks)
                    logger.info("QuestionGeneratorAgent: RAG context retrieved successfully", chunk_count=len(chunks))
            except Exception as e:
                logger.warning("QuestionGeneratorAgent: RAG retrieval failed, proceeding without context", error=str(e))

        # 2. Invoke LLM with Prompts
        prompt = TASK_PROMPT.format(
            candidate_profile=profile.model_dump_json(indent=2),
            job_requirements=requirement.model_dump_json(indent=2),
            skill_gap=skill_gap.model_dump_json(indent=2),
            rag_context=rag_context or "No additional context retrieved."
        )

        response = self.llm_service.generate_structured_output(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=QuestionsList
        )
        logger.info("QuestionGeneratorAgent: Successfully generated questions", question_count=len(response.questions))
        return response.questions
