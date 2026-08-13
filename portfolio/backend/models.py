from typing import Optional
from pydantic import BaseModel


class Experience(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    skills_used: list[str] = []


class Resume(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    total_experience_years: Optional[float] = None
    skills: list[str] = []
    experiences: list[Experience] = []
    education: list[str] = []
    projects: list[str] = []
    certifications: list[str] = []
    achievements: list[str] = []

class PersonalProfile(BaseModel):
    """Everything about you that ISN'T in your resume — the kind of thing
    an interviewer asks that a resume can't answer. Loaded directly from
    profile_data.json, never LLM-extracted, since you're stating it
    yourself rather than it being parsed from a document."""
 
    weaknesses: list[str] = []
    strengths: list[str] = []
    hobbies: list[str] = []
    five_year_vision: Optional[str] = None
    values: list[str] = []
    work_style: Optional[str] = None
    fun_facts: list[str] = []
    family_members: list[str] = []
    hire_me: list[str] = []

class ChatRequest(BaseModel):
    question: str