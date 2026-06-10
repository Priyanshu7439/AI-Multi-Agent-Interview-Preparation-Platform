from pydantic import BaseModel, Field
from typing import List

class JobRequirement(BaseModel):
    title: str = Field(..., description="Job title")
    required_skills: List[str] = Field(default_factory=list, description="Mandatory skills required for the role")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred or optional skills")
    responsibilities: List[str] = Field(default_factory=list, description="Key job responsibilities")
    qualifications: List[str] = Field(default_factory=list, description="Required education or certifications")
    keywords: List[str] = Field(default_factory=list, description="Key terms and buzzwords for ATS search")
