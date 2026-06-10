from typing import Type, TypeVar
from langchain_google_genai import ChatGoogleGenerativeAI
from app.domain.interfaces.llm_service import ILLMService
from app.core.config import settings
from app.core.exceptions import LLMException
from app.core.logging import logger

T = TypeVar("T")

class GeminiLLMService(ILLMService):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        try:
            self.model_name = model_name
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.2
            )
            logger.info("Gemini LLM Service initialized", model=model_name)
        except Exception as e:
            logger.error("Failed to initialize Gemini LLM Service", error=str(e))
            raise LLMException(f"LLM initialization failed: {str(e)}")

    def generate_structured_output(
        self, 
        prompt: str, 
        system_prompt: str, 
        response_model: Type[T]
    ) -> T:
        try:
            structured_llm = self.llm.with_structured_output(response_model)
            messages = [
                ("system", system_prompt),
                ("user", prompt)
            ]
            response = structured_llm.invoke(messages)
            return response
        except Exception as e:
            logger.error("Structured generation failed", model=self.model_name, error=str(e))
            raise LLMException(f"LLM structured generation failed: {str(e)}")

    def generate_text(
        self, 
        prompt: str, 
        system_prompt: str
    ) -> str:
        try:
            messages = [
                ("system", system_prompt),
                ("user", prompt)
            ]
            response = self.llm.invoke(messages)
            return str(response.content)
        except Exception as e:
            logger.error("Text generation failed", model=self.model_name, error=str(e))
            raise LLMException(f"LLM text generation failed: {str(e)}")
