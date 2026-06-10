from abc import ABC, abstractmethod
from typing import Type, TypeVar, Any

T = TypeVar("T")

class ILLMService(ABC):
    @abstractmethod
    def generate_structured_output(
        self, 
        prompt: str, 
        system_prompt: str, 
        response_model: Type[T]
    ) -> T:
        """Generate a structured Pydantic object from the LLM.

        Args:
            prompt: Task or user prompt.
            system_prompt: System context/instruction.
            response_model: Pydantic model class to conform output to.

        Returns:
            An instance of response_model.
        """
        pass

    @abstractmethod
    def generate_text(
        self, 
        prompt: str, 
        system_prompt: str
    ) -> str:
        """Generate raw text response from the LLM.

        Args:
            prompt: Task or user prompt.
            system_prompt: System context/instruction.

        Returns:
            Raw text string.
        """
        pass
