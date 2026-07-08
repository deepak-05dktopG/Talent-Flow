"""
routers/applications.py - candidate application management API endpoints
========================================================================
This file is the core controller for candidate applications. It handles:
1. Parsing resumes submitted by candidates (extracting skills, experience, education).
2. Creating new applications when candidates apply through a job page.
3. Listing and sorting applications with search filters on the HR dashboard.
4. Performing single and bulk status updates (e.g. Shortlisted, Rejected, Offered, Hired).
5. Fetching auto-generated, AI-powered interview questions relative to the candidate's resume.
6. Displaying resume file previews (.pdf, .docx, .txt).
"""

import os
import uuid
import tempfile
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import FileResponse
from app.schemas import ApplicationCreate, BulkStatusUpdate
from app.database import jobs_collection, applications_collection
from app.utils.auth import get_current_user
from app.services import parser_service, ai_service, email_service
from app.services.storage_service import upload_resume
from app import config
from datetime import datetime
from typing import Optional

# Router handles candidates and dashboard actions
router = APIRouter(tags=["applications"])

@router.post("/api/apply/parse-resume")
async def parse_resume_only(
    resume: UploadFile = File(...),
    job_id: Optional[str] = Query(None)
):
    """
    Utility endpoint that reads and parses a resume file on-the-fly.
    
    Used by the candidate application frontend to auto-fill the form fields
    (name, email, phone, etc.) as soon as the candidate uploads their file.
    
    Steps:
    1. Validate file extension (only PDF, DOCX, TXT allowed)
    2. Write uploaded bytes to a temporary directory file
    3. Run parser_service to extract resume details
    4. Check if a candidate with the same email/phone already applied to avoid duplicates
    5. Clean up the temp file and return the parsed JSON data
    """
    # Restrict uploads to common document formats
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    if resume.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are accepted")

    file_bytes = await resume.read()

    # Save to transient temp file so the parser service can read it from path
    suffix = os.path.splitext(resume.filename)[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        parsed = parser_service.parse_resume(tmp_path)
    except Exception as e:
        print(f"Resume parsing exception: {e}")
        # Return fallback empty structure on error
        parsed = {"name": "", "email": "", "phone": "", "linkedin": "", "github": "", "skills": [], "education": "", "experience": ""}
    finally:
        # Guarantee removal of the temporary file from hard disk
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # Check for existing parallel application if job_id is submitted
    if job_id:
        email = parsed.get("email")
        phone = parsed.get("phone")
        duplicate_query = {"job_id": job_id}
        conditions = []
        if email:
            conditions.append({"email": email})
        if phone:
            conditions.append({"phone": phone})
            
        if conditions:
            duplicate_query["$or"] = conditions
            existing = await applications_collection.find_one(duplicate_query)
            if existing:
                parsed["is_duplicate"] = True
                parsed["duplicate_message"] = "We have received your information already; you cannot apply for this position."

    return parsed

@router.post("/api/apply/{job_id}", status_code=201)
async def submit_application(
    job_id: str,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    linkedin: str = Form(""),
    github: str = Form(""),
    portfolio: str = Form(""),
    resume: UploadFile = File(...)
):
    """
    Stores a candidate's formal application in the database.
    
    Steps:
    1. Verify the job is active/open
    2. Check for duplicate submissions by email or phone
    3. Run parser service on resume file
    4. Upload resume file to Cloudinary (or local storage fallback)
    5. Run AI screening matching models (match score, summary explanation, career paths, strengths)
    6. Save app document to MongoDB 'applications'
    7. Trigger background email confirming application receipt
    """
    # 1. Verify target job is open
    job = await jobs_collection.find_one({"_id": job_id, "is_active": True})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or is no longer active")

    # 2. Check for duplicates
    duplicate_query = {"job_id": job_id}
    conditions = []
    if email:
        conditions.append({"email": email})
    if phone:
        conditions.append({"phone": phone})
        
    if conditions:
        duplicate_query["$or"] = conditions
        existing = await applications_collection.find_one(duplicate_query)
        if existing:
            raise HTTPException(status_code=400, detail="We have your information already, you cannot apply for this position.")

    # 3. Validate resume document type
    allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
    if resume.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are accepted")

    file_bytes = await resume.read()

    # 4. Parse text extraction
    suffix = os.path.splitext(resume.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        parsed = parser_service.parse_resume(tmp_path)
    except Exception as e:
        print(f"Resume parse error: {e}")
        parsed = {"name": name, "email": email, "phone": phone, "skills": [], "education": "", "experience": "", "raw_text": ""}
    finally:
        os.unlink(tmp_path)

    # 5. Upload resume storage (secure file retrieval link generation)
    storage_result = upload_resume(file_bytes, resume.filename, resume.content_type)
    resume_url = storage_result["url"]

    # 6. Apply AI matching heuristics/APIs to rank the candidate details
    try:
        ai_result = ai_service.score_and_match_candidate(parsed, job["job_description"], job["required_skills"])
        summary = ai_service.generate_resume_summary(parsed)
    except Exception as e:
        print(f"AI analysis error: {e}")
        ai_result = {"match_score": 50, "match_explanation": "Analysis pending due to system load", "strengths": [], "missing_skills": [], "career_path": []}
        summary = f"Candidate {name} applied for {job['title']}."

    # 7. Package and write candidate record to MongoDB
    app_id = str(uuid.uuid4())
    app_doc = {
        "_id": app_id,
        "job_id": job_id,
        "job_title": job["title"],
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
        "resume_url": resume_url,
        "parsed_skills": parsed.get("skills", []),
        "parsed_experience": parsed.get("experience", ""),
        "parsed_education": parsed.get("education", ""),
        "ai_summary": summary,
        "match_score": ai_result.get("match_score", 0),
        "match_explanation": ai_result.get("match_explanation", ""),
        "strengths": ai_result.get("strengths", []),
        "missing_skills": ai_result.get("missing_skills", []),
        "career_path": ai_result.get("career_path", []),
        "status": "applied",
        "applied_at": datetime.utcnow().isoformat(),
        "created_by": job["created_by"]
    }
    await applications_collection.insert_one(app_doc)

    # 8. Trigger confirmation notification asynchronously
    background_tasks.add_task(email_service.send_application_received_email, email, name, job["title"])

    return {"message": "Application submitted successfully!", "application_id": app_id}

@router.get("/api/applications")
async def list_applications(
    current_user: dict = Depends(get_current_user),
    job_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("match_score")
):
    """
    Returns filterable and searchable candidate applications for HR recruiters.
    
    Query filters:
    - job_id: list applicants for a specific post
    - status: filter by pipeline stage (e.g. shortlisted, rejected, hired)
    - search: search candidates by name, email, skills, or job title
    - sort_by: sort lists by 'match_score' (default) or 'applied_at' (newest)
    """
    query = {"created_by": current_user["user_id"]}
    if job_id:
        query["job_id"] = job_id
    if status_filter:
        query["status"] = status_filter

    cursor = applications_collection.find(query)
    apps = await cursor.to_list(length=500)

    # Filter by search string if requested
    if search:
        search_lower = search.lower()
        apps = [
            a for a in apps
            if search_lower in a.get("name", "").lower()
            or search_lower in a.get("email", "").lower()
            or search_lower in " ".join(a.get("parsed_skills", [])).lower()
            or search_lower in a.get("job_title", "").lower()
            or search_lower in a.get("status", "").lower()
        ]

    # Sort applications chronologically or by match score
    reverse = True
    key = sort_by if sort_by in ["match_score", "applied_at"] else "match_score"
    apps.sort(key=lambda x: x.get(key, 0) if key == "match_score" else x.get(key, ""), reverse=reverse)

    return {"applications": apps, "total": len(apps)}

@router.get("/api/applications/{app_id}")
async def get_application(app_id: str, current_user: dict = Depends(get_current_user)):
    """
    Fetches details of a specific candidate application.
    Also appends the hiring workflow stages configured for that position
    so the HR console knows which milestones are valid.
    """
    app = await applications_collection.find_one({"_id": app_id, "created_by": current_user["user_id"]})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Check parent Job configuration to pull custom round names
    job = await jobs_collection.find_one({"_id": app.get("job_id")})
    if job:
        app["hiring_rounds"] = job.get("hiring_rounds") or []
    else:
        app["hiring_rounds"] = []
        
    return app

@router.patch("/api/applications/{app_id}/status")
async def update_status(
    app_id: str,
    body: dict,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Updates the stage of an individual application.
    
    Steps:
    1. Fetch current application & associate job details
    2. Confirm requested target status is valid within candidate workflow rounds
    3. Save new status in MongoDB
    4. Auto-route specific email notifications:
       - Default templates for "shortlisted", "rejected", "offered", "custom"
       - Overridden template if the recruiter typed custom email body text from the UI
    """
    new_status = body.get("status")
    app = await applications_collection.find_one({"_id": app_id, "created_by": current_user["user_id"]})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    # Read job custom stages (if any exist) to ensure the status change is valid
    job = await jobs_collection.find_one({"_id": app.get("job_id")})
    allowed_rounds = ["applied", "rejected", "hired"]
    hiring_rounds_source = job.get("hiring_rounds") if (job and job.get("hiring_rounds")) else []
    if not hiring_rounds_source:
        # Default pipeline fallback
        hiring_rounds_source = ["Shortlisted", "Technical Interview", "HR Round", "Offered"]
        
    for r in hiring_rounds_source:
        allowed_rounds.append(r.lower())
        
    if new_status.lower() not in allowed_rounds:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {allowed_rounds}")

    # Save to DB
    await applications_collection.update_one({"_id": app_id}, {"$set": {"status": new_status}})

    # Trigger email notifications
    send_email = body.get("send_email", True)
    custom_body = body.get("email_body", None)

    if send_email:
        state = new_status.lower()
        if custom_body:
            # Generate matching subjects based on candidate category
            subject = f"Application Update: Stage '{new_status}' for {app['job_title']}"
            if state == "shortlisted":
                 subject = f"Congratulations! You've been Shortlisted for {app['job_title']}"
            elif state == "rejected":
                 subject = f"Application Update: {app['job_title']}"
            elif state in ["offered", "offer"]:
                 subject = f"Job Offer: {app['job_title']} - TalentFlow"
                 
            background_tasks.add_task(email_service.send_custom_body_email, app["email"], subject, custom_body)
        else:
            # Send standard templates
            if state == "shortlisted":
                 background_tasks.add_task(email_service.send_shortlisted_email, app["email"], app["name"], app["job_title"])
            elif state == "rejected":
                 background_tasks.add_task(email_service.send_rejected_email, app["email"], app["name"], app["job_title"])
            elif state in ["offered", "offer"]:
                 background_tasks.add_task(email_service.send_offer_email, app["email"], app["name"], app["job_title"])
            elif state in ["applied", "hired", "interview_scheduled"]:
                 if state == "hired":
                      background_tasks.add_task(email_service.send_custom_round_email, app["email"], app["name"], app["job_title"], new_status)
            else:
                 background_tasks.add_task(email_service.send_custom_round_email, app["email"], app["name"], app["job_title"], new_status)

    return {"message": f"Status updated to {new_status}"}

@router.get("/api/applications/{app_id}/questions")
async def generate_questions(
    app_id: str,
    difficulty: str = Query("Medium"),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns AI-generated technical interview questions designed specifically for a candidate's resume.
    Recruiters can adjust difficulty (Easy, Medium, Hard).
    """
    app = await applications_collection.find_one({"_id": app_id, "created_by": current_user["user_id"]})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    parsed_info = {
        "skills": app.get("parsed_skills", []),
        "experience": app.get("parsed_experience", ""),
        "education": app.get("parsed_education", ""),
        "raw_text": ""
    }
    # Invoke AI helper
    questions = ai_service.generate_interview_questions(parsed_info, difficulty)
    return {"questions": questions, "difficulty": difficulty}

@router.get("/api/applications/{app_id}/resume-preview")
async def preview_resume(app_id: str, token: Optional[str] = Query(None), current_user: dict = Depends(get_current_user)):
    """
    Renders/downloads the candidate's uploaded resume.
    If Cloudinary is active: returns a RedirectResponse directing the browser to the Cloudinary URL.
    If local storage is active: reads the file from local uploads directory and streams it inline.
    """
    app = await applications_collection.find_one({"_id": app_id, "created_by": current_user["user_id"]})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    resume_url = app.get("resume_url")
    if not resume_url:
        raise HTTPException(status_code=404, detail="Resume not found for this candidate")
        
    # Redirect if it's hosted externally (e.g. Cloudinary)
    if resume_url.startswith("http://") or resume_url.startswith("https://"):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(resume_url)
            
    # Serve locally stored folders
    filename = resume_url.split("/")[-1]
    file_path = os.path.join(config.UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
        
    media_type = "application/pdf"
    if filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".txt"):
        media_type = "text/plain"
        
    return FileResponse(file_path, media_type=media_type, content_disposition_type="inline")

@router.get("/api/resumes/{filename}")
async def serve_resume(filename: str):
    """
    Public static file serving route for local development. Serves local resume files
    from the backend uploads folder.
    """
    file_path = os.path.join(config.UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    media_type = "application/pdf"
    if filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".txt"):
        media_type = "text/plain"
    return FileResponse(file_path, media_type=media_type, content_disposition_type="inline")

@router.patch("/api/applications/bulk-status")
async def bulk_update_status(
    body: BulkStatusUpdate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Updates the stage of multiple candidates at the same time.
    
    Used when HR recruiters select multiple candidates on the dashboard list
    and perform a bulk status update.
    
    Supports:
    - Custom parameterized email body (e.g., recruiter writes 'Hello {name}...').
      The backend replaces '{name}' and '{job_title}' with candidate-specific details.
    """
    if not body.application_ids:
        raise HTTPException(status_code=400, detail="No candidate IDs provided")
        
    updated_count = 0
    for app_id in body.application_ids:
        app = await applications_collection.find_one({"_id": app_id, "created_by": current_user["user_id"]})
        if not app:
            continue
            
        # Verify valid status against job stage settings
        job = await jobs_collection.find_one({"_id": app.get("job_id")})
        allowed_rounds = ["applied", "rejected", "hired"]
        hiring_rounds_source = job.get("hiring_rounds") if (job and job.get("hiring_rounds")) else []
        if not hiring_rounds_source:
            hiring_rounds_source = ["Shortlisted", "Technical Interview", "HR Round", "Offered"]
            
        for r in hiring_rounds_source:
            allowed_rounds.append(r.lower())
            
        if body.status.lower() not in allowed_rounds:
            raise HTTPException(
                status_code=400, 
                detail=f"Status '{body.status}' is not allowed for candidate '{app['name']}' (Job: '{app['job_title']}')"
            )
            
        # Update MongoDB record
        await applications_collection.update_one({"_id": app_id}, {"$set": {"status": body.status}})
        updated_count += 1
        
        # Schedule personalized notifications in the background
        if body.send_email:
            state = body.status.lower()
            
            # Replace placeholder variables with candidate-specific data
            candidate_body = None
            if body.email_body:
                candidate_body = body.email_body.replace("{name}", app["name"]).replace("{job_title}", app["job_title"])
                
            if candidate_body:
                subject = f"Application Update: Stage '{body.status}' for {app['job_title']}"
                if state == "shortlisted":
                     subject = f"Congratulations! You've been Shortlisted for {app['job_title']}"
                elif state == "rejected":
                     subject = f"Application Update: {app['job_title']}"
                elif state in ["offered", "offer"]:
                     subject = f"Job Offer: {app['job_title']} - TalentFlow"
                     
                background_tasks.add_task(email_service.send_custom_body_email, app["email"], subject, candidate_body)
            else:
                # Fallback to standard email templates
                if state == "shortlisted":
                     background_tasks.add_task(email_service.send_shortlisted_email, app["email"], app["name"], app["job_title"])
                elif state == "rejected":
                     background_tasks.add_task(email_service.send_rejected_email, app["email"], app["name"], app["job_title"])
                elif state in ["offered", "offer"]:
                     background_tasks.add_task(email_service.send_offer_email, app["email"], app["name"], app["job_title"])
                elif state in ["applied", "hired", "interview_scheduled"]:
                     if state == "hired":
                          background_tasks.add_task(email_service.send_custom_round_email, app["email"], app["name"], app["job_title"], body.status)
                else:
                     background_tasks.add_task(email_service.send_custom_round_email, app["email"], app["name"], app["job_title"], body.status)
                     
    return {"message": f"Successfully updated {updated_count} candidates"}
