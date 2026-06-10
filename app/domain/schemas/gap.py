from pydantic import BaseModel, Field
from typing import List

class SkillGap(BaseModel):
    missing_skills: List[str] = Field(default_factory=list, description="Skills required by the job but missing from the resume")
    matching_skills: List[str] = Field(default_factory=list, description="Skills matching between candidate and job description")
    match_percentage: float = Field(..., description="Overall skill match percentage between 0 and 100")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Concrete suggestions to bridge the identified gaps")
