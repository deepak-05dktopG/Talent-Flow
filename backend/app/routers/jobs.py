from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import JobCreate, JobUpdate
from app.database import jobs_collection
from app.utils.auth import get_current_user
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_job(job_data: JobCreate, current_user: dict = Depends(get_current_user)):
    job_id = str(uuid.uuid4())
    slug = job_data.title.lower().replace(" ", "-")
    
    # Compile job description from separate fields if not explicitly provided
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
    
    compiled_desc = "\n\n".join(desc_parts) if desc_parts else (job_data.job_description or "")
    if not compiled_desc:
        compiled_desc = "No description provided."

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
        "created_by": current_user["user_id"],
        "company_name": current_user["company_name"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "public_link": f"/apply/{slug}-{job_id[:8]}",
        
        # New optional split inputs
        "company_overview": job_data.company_overview,
        "role_summary": job_data.role_summary,
        "key_responsibilities": job_data.key_responsibilities,
        "required_qualifications": job_data.required_qualifications,
        "preferred_qualifications": job_data.preferred_qualifications,
        "skills_competencies": job_data.skills_competencies,
        "work_environment": job_data.work_environment,
        "compensation_benefits": job_data.compensation_benefits,
        "career_growth": job_data.career_growth,
        "hiring_rounds": job_data.hiring_rounds or [],
    }
    await jobs_collection.insert_one(job_doc)
    return {"message": "Job created successfully", "job": job_doc}

@router.get("")
async def list_jobs(current_user: dict = Depends(get_current_user)):
    cursor = jobs_collection.find({"created_by": current_user["user_id"]})
    jobs = await cursor.to_list(length=200)
    return {"jobs": jobs, "total": len(jobs)}

@router.get("/public/{job_slug}")
async def get_public_job(job_slug: str):
    """Public endpoint – no auth required. Used by candidate application form."""
    # Extract job ID fragment from slug (last 8 chars after last '-')
    parts = job_slug.rsplit("-", 1)
    if len(parts) < 2:
        raise HTTPException(status_code=404, detail="Job not found")
    job_id_fragment = parts[-1]

    # Find job whose _id starts with the fragment
    cursor = jobs_collection.find({"is_active": True})
    all_jobs = await cursor.to_list(length=500)
    matched_job = next((j for j in all_jobs if j["_id"].startswith(job_id_fragment)), None)

    if not matched_job:
        raise HTTPException(status_code=404, detail="Job not found or no longer active")

    # Return public subset with the optional structured fields
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
        
        # New optional split inputs
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
    job = await jobs_collection.find_one({"_id": job_id, "created_by": current_user["user_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}")
async def update_job(job_id: str, job_data: JobUpdate, current_user: dict = Depends(get_current_user)):
    job = await jobs_collection.find_one({"_id": job_id, "created_by": current_user["user_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    update_fields = {k: v for k, v in job_data.model_dump().items() if v is not None}
    if not update_fields:
        return {"message": "No fields to update"}
        
    # Check if any split fields changed, or if a recompile is needed
    has_split_change = any(k in update_fields for k in [
        "company_overview", "role_summary", "key_responsibilities",
        "required_qualifications", "preferred_qualifications", "skills_competencies",
        "work_environment", "compensation_benefits", "career_growth", "application_process"
    ])
    
    if has_split_change:
        desc_parts = []
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
        update_fields["job_description"] = compiled_desc

    await jobs_collection.update_one({"_id": job_id}, {"$set": update_fields})
    return {"message": "Job updated successfully", "job_id": job_id}

@router.delete("/{job_id}")
async def delete_job(job_id: str, current_user: dict = Depends(get_current_user)):
    job = await jobs_collection.find_one({"_id": job_id, "created_by": current_user["user_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await jobs_collection.delete_one({"_id": job_id})
    return {"message": "Job deleted successfully"}

@router.patch("/{job_id}/toggle")
async def toggle_job_status(job_id: str, current_user: dict = Depends(get_current_user)):
    job = await jobs_collection.find_one({"_id": job_id, "created_by": current_user["user_id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    new_status = not job.get("is_active", True)
    await jobs_collection.update_one({"_id": job_id}, {"$set": {"is_active": new_status}})
    return {"message": f"Job {'activated' if new_status else 'closed'}", "is_active": new_status}
