from app.domain.interfaces.llm_service import ILLMService
from app.domain.schemas import InterviewSession
from app.application.prompts.interview_prompts import SYSTEM_PROMPT, TASK_PROMPT
from app.core.logging import logger

class MockInterviewAgent:
    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service

    def generate_next_response(self, session: InterviewSession) -> str:
        """Formulate a professional and natural interviewer statement to present the next question."""
        logger.info("MockInterviewAgent: Generating conversational prompt")
        
        if session.current_question_index >= len(session.questions):
            return "The interview is now complete. Thank you for your responses! Please wait while we prepare your evaluation."

        current_q = session.questions[session.current_question_index].question_text

        # Format history to keep conversation state
        history_lines = []
        for i, ans in enumerate(session.answers):
            q_text = session.questions[i].question_text if i < len(session.questions) else ""
            history_lines.append(f"Interviewer: {q_text}")
            history_lines.append(f"Candidate: {ans.answer_text}")
        history_str = "\n".join(history_lines)

        prompt = TASK_PROMPT.format(
            current_question_index=session.current_question_index + 1,
            total_questions=len(session.questions),
            current_question=current_q,
            conversation_history=history_str or "Interview starting. No history yet."
        )

        response = self.llm_service.generate_text(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT
        )
        return response.strip()
