from typing import List
from app.domain.interfaces.llm_service import ILLMService
from app.domain.interfaces.vector_store import IVectorStoreService
from app.domain.schemas import InterviewQuestion, CandidateAnswer, EvaluationResult
from app.application.prompts.evaluation_prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.core.logging import logger

class EvaluationAgent:
    def __init__(self, llm_service: ILLMService, vector_store: IVectorStoreService = None):
        self.llm_service = llm_service
        self.vector_store = vector_store

    def evaluate(
        self, 
        session_id: str, 
        questions: List[InterviewQuestion], 
        answers: List[CandidateAnswer]
    ) -> EvaluationResult:
        """Evaluate candidate answers, scoring each question and summarizing performance."""
        logger.info("EvaluationAgent: Starting evaluation of mock session")

        # 1. RAG Context Retrieval
        rag_context = ""
        if self.vector_store:
            try:
                # Gather context for the primary questions in the session
                queries = [q.question_text for q in questions[:3]]
                chunks = []
                for query in queries:
                    match_chunks = self.vector_store.similarity_search(
                        collection_name=f"jd_{session_id}",
                        query=query,
                        k=2
                    )
                    chunks.extend(match_chunks)
                if chunks:
                    # Deduplicate chunks
                    rag_context = "\n\n".join(list(set(chunks)))
                    logger.info("EvaluationAgent: RAG context gathered", chunk_count=len(chunks))
            except Exception as e:
                logger.warning("EvaluationAgent: RAG context gathering failed, evaluating without RAG", error=str(e))

        # 2. Format inputs
        questions_str_list = []
        for q in questions:
            points = ", ".join(q.expected_points)
            questions_str_list.append(
                f"Question ID: {q.id}\nQuestion: {q.question_text}\nExpected Points: {points}\nCategory: {q.category}\nDifficulty: {q.difficulty}"
            )
        questions_str = "\n\n".join(questions_str_list)

        answers_str_list = []
        for ans in answers:
            answers_str_list.append(
                f"Question ID: {ans.question_id}\nAnswer: {ans.answer_text}"
            )
        answers_str = "\n\n".join(answers_str_list)

        # 3. Call LLM
        prompt = TASK_PROMPT.format(
            questions_with_expected_points=questions_str,
            candidate_answers=answers_str,
            rag_context=rag_context or "No additional context."
        )

        evaluation = self.llm_service.generate_structured_output(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            response_model=EvaluationResult
        )

        logger.info("EvaluationAgent: Evaluation completed successfully")
        return evaluation
