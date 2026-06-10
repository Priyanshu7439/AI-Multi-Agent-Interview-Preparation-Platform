from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any

class ExperienceItem(BaseModel):
    job_title: str = Field(..., description="Title of the job/position held")
    company: str = Field(..., description="Name of the company or organization")
    duration: Optional[str] = Field(None, description="Employment period, e.g., 'Jan 2020 - Dec 2022'")
    description: Optional[str] = Field(None, description="Description of responsibilities and achievements")

class ProjectItem(BaseModel):
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Brief description of the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies and libraries used in the project")

class EducationItem(BaseModel):
    degree: str = Field(..., description="Degree or certificate obtained")
    institution: str = Field(..., description="School, university, or academy name")
    graduation_year: Optional[str] = Field(None, description="Year of graduation")

class CandidateProfile(BaseModel):
    full_name: str = Field(..., description="Full name of the candidate")
    email: Optional[str] = Field(None, description="Email address of the candidate")
    phone: Optional[str] = Field(None, description="Phone number of the candidate")
    skills: List[str] = Field(default_factory=list, description="List of technical and soft skills")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Work experience items")
    projects: List[ProjectItem] = Field(default_factory=list, description="Project details")
    education: List[EducationItem] = Field(default_factory=list, description="Education details")
