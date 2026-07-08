"""
routers/jobs.py - Job Posting Management API Endpoints
========================================================
This file manages all operations related to job postings that recruiters create.

Endpoints:
  POST   /api/jobs                     — Create a new job posting (requires login)
  GET    /api/jobs                     — List all jobs created by the logged-in recruiter
  GET    /api/jobs/public/{job_slug}   — Get a specific job (PUBLIC — no login required, for candidates)
  GET    /api/jobs/{job_id}            — Get a specific job (requires login)
  PUT    /api/jobs/{job_id}            — Edit an existing job posting (requires login)
  DELETE /api/jobs/{job_id}            — Permanently delete a job (requires login)
  PATCH  /api/jobs/{job_id}/toggle     — Toggle a job between Active (open) and Closed (requires login)

Key concepts:
- Each job has a 'public_link' (e.g. /apply/senior-developer-a1b2c3d4) that candidates
  use to view and apply for a job through the public application form.
- The 'is_active' field controls whether a job is open to new applications.
- The job description is compiled automatically from separate structured text fields
  (company_overview, role_summary, key_responsibilities, etc.) into a single readable document.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import JobCreate, JobUpdate
from app.database import jobs_collection
from app.utils.auth import get_current_user
from datetime import datetime
import uuid

# All routes in this file are prefixed with /api/jobs
router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_job(job_data: JobCreate, current_user: dict = Depends(get_current_user)):
    """
    Creates a new job posting and stores it in MongoDB.
    
    Steps:
    1. Generate a unique job ID and a URL-friendly "slug" from the title
    2. Compile all structured text fields (overview, responsibilities, etc.) into one combined description
    3. Build the full job document and save to the 'jobs' collection
    4. Return the saved job with its auto-generated public application link
    """
    job_id = str(uuid.uuid4())   # Unique ID for this job (used in MongoDB and public URL)
    # Create a URL-safe slug from the job title (e.g., "Senior Developer" → "senior-developer")
    slug = job_data.title.lower().replace(" ", "-")
    
    # Compile the full job description from separate structured fields.
    # If the recruiter fills in specific sections, we concatenate them with headers.
    # If not, we fall back to the raw job_description field.
    desc_parts = []
    if job_data.company_overview:
        desc_parts.append(f"Company Overview:\n{job_data.company_overview}")
    if job_data.role_summary:
        desc_parts.append(f"Role Summary:\n{job_data.role_summary}")
    if job_data.key_responsibilities:
        desc_parts.append(f"Key Responsibilities:\n{job_data.key_responsibilities}")
    if job_data.required_qualifications:
        desc_parts.append(f"Required Qualifications:\n{job_data.required_qualifications}")
    if job_data.preferred_qualifications:
        desc_parts.append(f"Preferred Qualifications:\n{job_data.preferred_qualifications}")
    if job_data.skills_competencies:
        desc_parts.append(f"Skills & Competencies:\n{job_data.skills_competencies}")
    if job_data.work_environment:
        desc_parts.append(f"Work Environment:\n{job_data.work_environment}")
    if job_data.compensation_benefits:
        desc_parts.append(f"Compensation & Benefits:\n{job_data.compensation_benefits}")
    if job_data.career_growth:
        desc_parts.append(f"Career Growth:\n{job_data.career_growth}")
    
    # Join all sections with blank lines between them, or fall back to plain description
    compiled_desc = "\n\n".join(desc_parts) if desc_parts else (job_data.job_description or "")
    if not compiled_desc:
        compiled_desc = "No description provided."

    # Build the complete job document ready to save in MongoDB
    job_doc = {
        "_id": job_id,
        "title": job_data.title,
        "department": job_data.department,
        "experience": job_data.experience,
        "location": job_data.location,
        "employment_type": job_data.employment_type,
        "salary": job_data.salary,
        "job_description": compiled_desc,
        "required_skills": job_data.required_skills,
        "deadline": job_data.deadline,
        "created_by": current_user["user_id"],       # Which recruiter owns this job
        "company_name": current_user["company_name"],# Auto-filled from the recruiter's profile
        "is_active": True,                           # Job is open by default after creation
        "created_at": datetime.utcnow().isoformat(),
        # Public shareable URL — includes first 8 chars of job ID to ensure uniqueness
        "public_link": f"/apply/{slug}-{job_id[:8]}",
        # Preserve all structured fields as separate columns too
        "company_overview": job_data.company_overview,
        "role_summary": job_data.role_summary,
        "key_responsibilities": job_data.key_responsibilities,
        "required_qualifications": job_data.required_qualifications,
        "preferred_qualifications": job_data.preferred_qualifications,
        "skills_competencies": job_data.skills_competencies,
        "work_environment": job_data.work_environment,
        "compensation_benefits": job_data.compensation_benefits,
        "career_growth": job_data.career_growth,
        "hiring_rounds": job_data.hiring_rounds or [],  # The ordered list of interview stages for this role
    }
    await jobs_collection.insert_one(job_doc)  # Save to MongoDB
    return {"message": "Job created successfully", "job": job_doc}

@router.get("")
async def list_jobs(current_user: dict = Depends(get_current_user)):
    """
    Returns all job postings created by the logged-in recruiter.
    Only shows this recruiter's own jobs (not other companies' jobs).
    """
    cursor = jobs_collection.find({"created_by": current_user["user_id"]})
    jobs = await cursor.to_list(length=200)  # Load up to 200 jobs
    return {"jobs": jobs, "total": len(jobs)}

@router.get("/public/{job_slug}")
async def get_public_job(job_slug: str):
    """
    PUBLIC endpoint — no login required.
    Used by candidates visiting the public apply page to view job details.
    
    How the job is found:
    - The URL slug contains the first 8 characters of the job ID at the end (e.g., "senior-dev-a1b2c3d4")
    - We extract those 8 characters and search for a matching job ID in MongoDB
    """
    # Split the slug on the last "-" to extract the job ID fragment
    parts = job_slug.rsplit("-", 1)
    if len(parts) < 2:
        raise HTTPException(status_code=404, detail="Job not found")
    job_id_fragment = parts[-1]  # e.g., "a1b2c3d4"

    # Search through all active jobs to find one whose ID starts with the fragment
    cursor = jobs_collection.find({"is_active": True})
    all_jobs = await cursor.to_list(length=500)
    matched_job = next((j for j in all_jobs if j["_id"].startswith(job_id_fragment)), None)

    if not matched_job:
        raise HTTPException(status_code=404, detail="Job not found or no longer active")

    # Return a safe public subset — omits internal recruiter info like created_by
    return {
        "id": matched_job["_id"],
        "title": matched_job["title"],
        "department": matched_job["department"],
        "location": matched_job["location"],
        "employment_type": matched_job["employment_type"],
        "experience": matched_job["experience"],
        "salary": matched_job.get("salary"),
        "job_description": matched_job["job_description"],
        "required_skills": matched_job["required_skills"],
        "deadline": matched_job["deadline"],
        "company_name": matched_job["company_name"],
        "company_overview": matched_job.get("company_overview"),
        "role_summary": matched_job.get("role_summary"),
        "key_responsibilities": matched_job.get("key_responsibilities"),
        "required_qualifications": matched_job.get("required_qualifications"),
        "preferred_qualifications": matched_job.get("preferred_qualifications"),
        "skills_competencies": matched_job.get("skills_competencies"),
        "work_environment": matched_job.get("work_environment"),
        "compensation_benefits": matched_job.get("compensation_benefits"),
        "career_growth": matched_job.get("career_growth"),
        "application_process": matched_job.get("application_process"),
    }

@router.get("/{job_id}")
async def get_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Returns a specific job posting by its ID (for the logged-in recruiter only)."""
    job = await jobs_collection.find_one({"_id": job_id, "created_by": current_user["user_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}")
async def update_job(job_id: str, job_data: JobUpdate, current_user: dict = Depends(get_current_user)):
    """
    Updates an existing job posting with new data.
    
    Special logic: If any of the structured text sections are updated, the compiled
    'job_description' field is automatically recompiled to stay in sync.
    Only non-null fields in the request body are applied to minimize accidental overwrites.
    """
    job = await jobs_collection.find_one({"_id": job_id, "created_by": current_user["user_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Only include fields that were actually provided (not None) in the update operation
    update_fields = {k: v for k, v in job_data.model_dump().items() if v is not None}
    if not update_fields:
        return {"message": "No fields to update"}
        
    # If any structured section changed, recompile the full job_description from all sections
    has_split_change = any(k in update_fields for k in [
        "company_overview", "role_summary", "key_responsibilities",
        "required_qualifications", "preferred_qualifications", "skills_competencies",
        "work_environment", "compensation_benefits", "career_growth", "application_process"
    ])
    
    if has_split_change:
        desc_parts = []
        # Try to use updated value first; if not updated, use the existing DB value
        fields_to_check = [
            ("Company Overview", "company_overview"),
            ("Role Summary", "role_summary"),
            ("Key Responsibilities", "key_responsibilities"),
            ("Required Qualifications", "required_qualifications"),
            ("Preferred Qualifications", "preferred_qualifications"),
            ("Skills & Competencies", "skills_competencies"),
            ("Work Environment", "work_environment"),
            ("Compensation & Benefits", "compensation_benefits"),
            ("Career Growth", "career_growth")
        ]
        for header, key in fields_to_check:
            val = update_fields.get(key) if key in update_fields else job.get(key)
            if val:
                desc_parts.append(f"{header}:\n{val}")
                
        compiled_desc = "\n\n".join(desc_parts) if desc_parts else (update_fields.get("job_description") or job.get("job_description") or "")
        if not compiled_desc:
            compiled_desc = "No description provided."
        update_fields["job_description"] = compiled_desc  # Write recompiled description

    await jobs_collection.update_one({"_id": job_id}, {"$set": update_fields})
    return {"message": "Job updated successfully", "job_id": job_id}

@router.delete("/{job_id}")
async def delete_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """Permanently deletes a job posting from the database. This action is irreversible."""
    job = await jobs_collection.find_one({"_id": job_id, "created_by": current_user["user_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await jobs_collection.delete_one({"_id": job_id})
    return {"message": "Job deleted successfully"}

@router.patch("/{job_id}/toggle")
async def toggle_job_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """
    Switches a job between Active (open) and Closed (not accepting applications).
    
    Active  (is_active=True)  → New candidates can apply via the public link
    Closed (is_active=False) → Public apply page is hidden; no new applications
    """
    job = await jobs_collection.find_one({"_id": job_id, "created_by": current_user["user_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    new_status = not job.get("is_active", True)  # Flip the current status
    await jobs_collection.update_one({"_id": job_id}, {"$set": {"is_active": new_status}})
    return {"message": f"Job {'activated' if new_status else 'closed'}", "is_active": new_status}
