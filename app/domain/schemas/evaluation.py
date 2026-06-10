from pydantic import BaseModel, Field
from typing import List, Dict, Any

class QuestionFeedback(BaseModel):
    question_id: str = Field(..., description="ID of the question evaluated")
    score: float = Field(..., description="Score for this answer, usually 1 to 10")
    explanation: str = Field(..., description="Detailed explanation of the score and performance")
    sample_good_answer: str = Field(..., description="Example of a high-quality answer for this question")

class EvaluationResult(BaseModel):
    scores: Dict[str, float] = Field(default_factory=dict, description="Question scores and the computed overall score")
    weaknesses: List[str] = Field(default_factory=list, description="Weaknesses identified in the candidate's answers")
    strengths: List[str] = Field(default_factory=list, description="Strengths identified in the candidate's answers")
    feedback: List[QuestionFeedback] = Field(default_factory=list, description="Feedback per question")
