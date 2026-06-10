from pydantic import BaseModel, Field
from typing import List

class InterviewQuestion(BaseModel):
    id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="The interview question text")
    category: str = Field(..., description="Category: technical, behavioral, project-based, or role-specific")
    difficulty: str = Field(..., description="Difficulty level: beginner, intermediate, or advanced")
    expected_points: List[str] = Field(default_factory=list, description="Key points expected in the answer")
