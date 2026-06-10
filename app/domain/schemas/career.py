from pydantic import BaseModel, Field
from typing import List, Dict, Any

class RecommendedProject(BaseModel):
    name: str = Field(..., description="Name of the recommended project")
    description: str = Field(..., description="Description of the project and why it helps")
    target_skills: List[str] = Field(default_factory=list, description="Skills this project will help develop")

class CareerAdvice(BaseModel):
    roadmap: List[str] = Field(default_factory=list, description="Step-by-step learning roadmap")
    recommended_projects: List[RecommendedProject] = Field(default_factory=list, description="Recommended portfolio projects")
    recommended_certifications: List[str] = Field(default_factory=list, description="Recommended courses or certifications")
    general_tips: List[str] = Field(default_factory=list, description="General job search and interview tips")
