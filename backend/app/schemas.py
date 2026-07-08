"""
schemas.py - Data Validation Models
=====================================
This file defines the exact "shape" of data that flows into and out of our API.
Think of these as fill-in forms — each form specifies exactly what fields are required
and what type of data is accepted (text, number, email, list, etc.).

When a request comes in, FastAPI automatically checks the data against these models
and rejects anything that doesn't match, keeping our database clean and safe.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# ══════════════════════════════════════════════
# AUTHENTICATION SCHEMAS (Login & Registration)
# ══════════════════════════════════════════════

class UserRegister(BaseModel):
    """Data required when an HR recruiter creates a new account."""
    email: EmailStr           # Must be a valid email format (e.g., hr@company.com)
    password: str = Field(..., min_length=6)  # Password must be at least 6 characters
    company_name: str = Field(..., min_length=2)  # Company name (at least 2 characters)
    phone: Optional[str] = None   # Phone number is optional
    role: str = "hr"              # Default role is "hr" (Human Resources)

class UserLogin(BaseModel):
    """Data required when an HR recruiter logs in."""
    email: EmailStr    # The recruiter's registered email
    password: str      # Their plain-text password (will be checked against the hashed version)

class UserResponse(BaseModel):
    """Data returned to the frontend after a successful login or profile fetch.
    Never includes the password — only safe, public user information."""
    id: str = Field(..., alias="_id")  # MongoDB uses "_id" but we expose it as "id"
    email: EmailStr
    company_name: str
    phone: Optional[str] = None
    role: str

    class Config:
        populate_by_name = True   # Allow both "id" and "_id" field names
        json_encoders = {datetime: lambda v: v.isoformat()}  # Convert dates to readable strings

class Token(BaseModel):
    """The JWT login token returned after successful authentication.
    The frontend stores this token and sends it with every future request to prove identity."""
    access_token: str   # The actual token string (a long encoded string)
    token_type: str     # Always "bearer" — this tells the backend how to read the token

class TokenData(BaseModel):
    """The decoded contents of a JWT token — who is logged in."""
    email: Optional[str] = None    # The logged-in recruiter's email
    user_id: Optional[str] = None  # Their unique MongoDB user ID

# ══════════════════════════════════════════════
# JOB POSTING SCHEMAS
# ══════════════════════════════════════════════

class JobCreate(BaseModel):
    """Data required when an HR recruiter creates a new job posting."""
    title: str = Field(..., min_length=2)      # Job title (e.g., "Senior Python Developer")
    department: str = Field(..., min_length=2) # Department (e.g., "Engineering", "Marketing")
    experience: str   # Experience required (e.g., "2-5 years", "Entry level")
    location: str     # Work location (e.g., "Remote", "Bangalore", "Hybrid")
    employment_type: str  # Type of role (e.g., "Full-time", "Contract", "Internship")
    salary: Optional[str] = None              # Salary range — optional (e.g., "₹8-12 LPA")
    job_description: Optional[str] = None     # Full HTML/text description of the role
    required_skills: List[str]                # List of skills (e.g., ["Python", "FastAPI", "SQL"])
    deadline: str     # Application deadline in YYYY-MM-DD format
    hiring_rounds: Optional[List[str]] = None # Custom recruitment stages (e.g., ["Screening", "Technical", "HR"])
    # Optional extended job details for the public-facing job page:
    company_overview: Optional[str] = None         # About the company
    role_summary: Optional[str] = None             # Brief summary of the role
    key_responsibilities: Optional[str] = None     # What the candidate will do day-to-day
    required_qualifications: Optional[str] = None  # Must-have qualifications
    preferred_qualifications: Optional[str] = None # Nice-to-have qualifications
    skills_competencies: Optional[str] = None      # Technical and soft skills needed
    work_environment: Optional[str] = None         # Office/remote/hybrid culture
    compensation_benefits: Optional[str] = None    # Salary, perks, benefits
    career_growth: Optional[str] = None            # Growth opportunities within the company

class JobUpdate(BaseModel):
    """Data allowed when editing an existing job posting.
    All fields are optional — you only need to send what you want to change."""
    title: Optional[str] = None
    department: Optional[str] = None
    experience: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary: Optional[str] = None
    job_description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    deadline: Optional[str] = None
    is_active: Optional[bool] = None             # Set to False to close/hide the job posting
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
    """The full job posting data returned to the frontend when listing or viewing jobs."""
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
    created_by: str     # The HR User ID who created this job
    company_name: str   # Pre-filled from the recruiter's profile
    is_active: bool     # True = job is open; False = job is closed
    created_at: str     # Timestamp when the job was created
    public_link: str    # Auto-generated shareable URL for candidates to apply
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

# ══════════════════════════════════════════════
# CANDIDATE APPLICATION SCHEMAS
# ══════════════════════════════════════════════

class ApplicationCreate(BaseModel):
    """Personal details a candidate fills in when applying for a job.
    The resume file is uploaded separately as a form file attachment."""
    name: str = Field(..., min_length=2)   # Candidate's full name
    email: EmailStr                         # Their contact email
    phone: str                              # Phone number
    linkedin: Optional[str] = ""           # LinkedIn profile URL
    github: Optional[str] = ""            # GitHub profile URL
    portfolio: Optional[str] = ""         # Personal portfolio website URL

class ApplicationResponse(BaseModel):
    """The full application record returned to the HR dashboard.
    Includes AI-parsed information from the resume alongside the candidate's data."""
    id: str = Field(..., alias="_id")
    job_id: str                             # Which job was applied for
    job_title: str                          # Job title (cached for easy display)
    name: str
    email: EmailStr
    phone: str
    linkedin: Optional[str] = ""
    github: Optional[str] = ""
    portfolio: Optional[str] = ""
    resume_url: str                         # URL to the uploaded resume (Cloudinary or local)
    parsed_skills: List[str] = []          # Skills extracted by AI from the resume
    parsed_experience: Optional[str] = ""  # Work experience summary from the resume
    parsed_education: Optional[str] = ""   # Education details from the resume
    ai_summary: Optional[str] = ""         # AI-generated one-paragraph summary of the candidate
    match_score: int = 0                   # 0-100 score of how well the candidate fits the job
    match_explanation: Optional[str] = ""  # AI explanation of why the score was given
    strengths: List[str] = []             # Skills the candidate has that the job requires
    missing_skills: List[str] = []        # Skills the job requires but the candidate lacks
    career_path: List[str] = []           # AI-suggested career recommendations
    status: str = "applied"              # Current stage: applied → shortlisted → interview_scheduled → offered → hired / rejected
    applied_at: str                       # Timestamp when the application was submitted

    class Config:
        populate_by_name = True

# ══════════════════════════════════════════════
# INTERVIEW SCHEDULING SCHEMAS
# ══════════════════════════════════════════════

class InterviewCreate(BaseModel):
    """Data required when scheduling an interview for a candidate."""
    application_id: str     # Which application (candidate + job) this interview is for
    date_time: str          # Date and time of the interview (e.g., "2026-07-15 14:00")
    meeting_link: str       # Video call link (e.g., "https://zoom.us/j/1234567890")
    interviewer: str        # Name of the person conducting the interview (e.g., "John Doe - Eng Lead")
    send_email: bool = True          # Whether to email the candidate about the interview
    email_body: Optional[str] = None # Custom email body text — if provided, overrides the default template

class InterviewResponse(BaseModel):
    """Full interview record returned after scheduling."""
    id: str = Field(..., alias="_id")
    candidate_id: str       # MongoDB ID of the candidate
    application_id: str     # MongoDB ID of the application
    job_id: str
    job_title: str
    candidate_name: str
    candidate_email: str
    date_time: str
    meeting_link: str
    interviewer: str
    status: str = "scheduled"  # Status: "scheduled", "completed", or "cancelled"
    created_at: str

    class Config:
        populate_by_name = True

# ══════════════════════════════════════════════
# BULK & MISC SCHEMAS
# ══════════════════════════════════════════════

class CopilotQueryRequest(BaseModel):
    """A natural-language question sent to the AI Copilot assistant."""
    query: str   # e.g., "Show me all candidates with Python skills above 70% match"

class CopilotQueryResponse(BaseModel):
    """The AI Copilot's response to a natural-language question."""
    natural_response: str           # Human-readable answer
    suggested_action: Optional[str] = None  # A suggested follow-up action
    data: Optional[List[dict]] = None       # Any relevant data records found

class BulkStatusUpdate(BaseModel):
    """Data required to update many candidates' statuses at once."""
    application_ids: List[str]   # List of application IDs to update (selected on the dashboard)
    status: str                   # The new status to assign to all selected candidates
    send_email: bool = True       # Whether to email all candidates about the update
    email_body: Optional[str] = None  # Custom email body — supports {name} and {job_title} placeholders
