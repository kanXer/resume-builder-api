from pydantic import BaseModel
from typing import List, Optional


class Experience(BaseModel):
    company: str
    role: str
    duration: str
    points: List[str]


class Education(BaseModel):
    college: str
    degree: str
    year: str
    score: str


class ResumeData(BaseModel):

    name: str
    father_name: Optional[str] = None
    address: str
    phone: str
    email: Optional[str] = None
    github: Optional[str] = None

    dob: str
    languages: str
    hobbies: str

    strengths: List[str]
    certifications: List[str]

    education: List[Education]

    skills: Optional[List[str]] = None
    experience: Optional[List[Experience]] = None

    objective: Optional[str] = None