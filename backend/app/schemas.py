from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    company_name: str = Field(..., min_length=2)
    phone: Optional[str] = None
    role: str = "hr"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    company_name: str
    phone: Optional[str] = None
    role: str

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

# Job Schemas
class JobCreate(BaseModel):
    title: str = Field(..., min_length=2)
    department: str = Field(..., min_length=2)
    experience: str  # e.g., "2-5 years", "Entry level"
    location: str    # e.g., "Remote", "Bangalore"
    employment_type: str  # e.g., "Full-time", "Contract", "Internship"
    salary: Optional[str] = None
    job_description: Optional[str] = None
    required_skills: List[str]
    deadline: str    # YYYY-MM-DD
    hiring_rounds: Optional[List[str]] = None
    company_overview: Optional[str] = None
    role_summary: Optional[str] = None
    key_responsibilities: Optional[str] = None
    required_qualifications: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    skills_competencies: Optional[str] = None
    work_environment: Optional[str] = None
    compensation_benefits: Optional[str] = None
    career_growth: Optional[str] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    experience: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary: Optional[str] = None
    job_description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    deadline: Optional[str] = None
    is_active: Optional[bool] = None
    hiring_rounds: Optional[List[str]] = None
    company_overview: Optional[str] = None
    role_summary: Optional[str] = None
    key_responsibilities: Optional[str] = None
    required_qualifications: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    skills_competencies: Optional[str] = None
    work_environment: Optional[str] = None
    compensation_benefits: Optional[str] = None
    career_growth: Optional[str] = None

class JobResponse(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    department: str
    experience: str
    location: str
    employment_type: str
    salary: Optional[str] = None
    job_description: str
    required_skills: List[str]
    deadline: str
    created_by: str  # HR User ID
    company_name: str
    is_active: bool
    created_at: str
    public_link: str
    company_overview: Optional[str] = None
    role_summary: Optional[str] = None
    key_responsibilities: Optional[str] = None
    required_qualifications: Optional[str] = None
    preferred_qualifications: Optional[str] = None
    skills_competencies: Optional[str] = None
    work_environment: Optional[str] = None
    compensation_benefits: Optional[str] = None
    career_growth: Optional[str] = None

    class Config:
        populate_by_name = True

# Application & Candidate Schemas
class ApplicationCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""

class ApplicationResponse(BaseModel):
    id: str = Field(..., alias="_id")
    job_id: str
    job_title: str
    name: str
    email: EmailStr
    phone: str
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""
    resume_url: str
    parsed_skills: List[str] = []
    parsed_experience: Optional[str] = ""
    parsed_education: Optional[str] = ""
    ai_summary: Optional[str] = ""
    match_score: int = 0
    match_explanation: Optional[str] = ""
    strengths: List[str] = []
    missing_skills: List[str] = []
    career_path: List[str] = []
    status: str = "applied"  # applied, shortlisted, interview_scheduled, rejected, offered, hired
    applied_at: str

    class Config:
        populate_by_name = True

# Interview Schemas
class InterviewCreate(BaseModel):
    application_id: str
    date_time: str      # e.g., "2026-07-15 14:00"
    meeting_link: str    # e.g., "https://zoom.us/j/1234"
    interviewer: str     # e.g., "John Doe - Eng Lead"
    send_email: bool = True
    email_body: Optional[str] = None

class InterviewResponse(BaseModel):
    id: str = Field(..., alias="_id")
    candidate_id: str
    application_id: str
    job_id: str
    job_title: str
    candidate_name: str
    candidate_email: str
    date_time: str
    meeting_link: str
    interviewer: str
    status: str = "scheduled" # scheduled, completed, cancelled
    created_at: str

    class Config:
        populate_by_name = True

# Copilot Query Schema
class CopilotQueryRequest(BaseModel):
    query: str

class CopilotQueryResponse(BaseModel):
    natural_response: str
    suggested_action: Optional[str] = None
    data: Optional[List[dict]] = None

class BulkStatusUpdate(BaseModel):
    application_ids: List[str]
    status: str
    send_email: bool = True
    email_body: Optional[str] = None

