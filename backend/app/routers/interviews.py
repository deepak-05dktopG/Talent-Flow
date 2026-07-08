"""
routers/interviews.py - Interview Scheduling API Endpoints
===========================================================
This file manages all interview-related actions within the recruitment pipeline.

Endpoints:
  POST   /api/interviews                        — Schedule a new interview for a candidate
  GET    /api/interviews                        — List all interviews created by the logged-in recruiter
  PATCH  /api/interviews/{interview_id}/status  — Update interview status (scheduled/completed/cancelled)

How interview scheduling works:
1. HR selects a candidate from the dashboard and clicks "Schedule Interview"
2. They fill in the date, meeting link, and interviewer name (and optionally write a custom email)
3. This endpoint saves the interview record and automatically updates the candidate's status
   to "interview_scheduled" in the applications collection
4. An email is sent to the candidate — either a standardized template or the custom email
   the recruiter typed in the popup modal
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.schemas import InterviewCreate
from app.database import interviews_collection, applications_collection
from app.utils.auth import get_current_user
from app.services import email_service
from datetime import datetime
import uuid

# All routes prefixed with /api/interviews
router = APIRouter(prefix="/api/interviews", tags=["interviews"])

@router.post("", status_code=201)
async def schedule_interview(
    data: InterviewCreate,
    background_tasks: BackgroundTasks,     # Background tasks run AFTER the response is sent (non-blocking)
    current_user: dict = Depends(get_current_user)  # Ensures the recruiter is logged in
):
    """
    Schedules a new interview for a specific candidate application.
    
    Steps:
    1. Verify the application belongs to this recruiter (security check)
    2. Create an interview record in the 'interviews' collection
    3. Update the candidate's status to "interview_scheduled" in 'applications'
    4. Queue an email notification to the candidate in the background
       (so the API responds immediately while the email sends behind the scenes)
    """
    # Verify this application exists AND belongs to the current logged-in recruiter
    app = await applications_collection.find_one({"_id": data.application_id, "created_by": current_user["user_id"]})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Build the interview record to save to MongoDB
    interview_doc = {
        "_id": str(uuid.uuid4()),                  # Unique ID for this interview
        "candidate_id": app["_id"],                # Reference to the candidate's application
        "application_id": data.application_id,
        "job_id": app["job_id"],                   # Which job position this is for
        "job_title": app["job_title"],
        "candidate_name": app["name"],
        "candidate_email": app["email"],
        "date_time": data.date_time,               # When the interview is scheduled
        "meeting_link": data.meeting_link,         # Zoom/Google Meet link etc.
        "interviewer": data.interviewer,           # Name of the person conducting the interview
        "status": "scheduled",                     # Initial status
        "created_by": current_user["user_id"],     # Which recruiter created this
        "created_at": datetime.utcnow().isoformat()
    }
    await interviews_collection.insert_one(interview_doc)  # Save interview to database

    # Automatically update the candidate's application status to "interview_scheduled"
    await applications_collection.update_one(
        {"_id": data.application_id},
        {"$set": {"status": "interview_scheduled"}}
    )

    # Send an email notification to the candidate (runs in background, doesn't block the response)
    if data.send_email:
        if data.email_body:
            # If HR typed a custom email body in the modal, send that instead
            background_tasks.add_task(
                email_service.send_custom_body_email,
                app["email"],
                f"Interview Scheduled: {app['job_title']}",
                data.email_body
            )
        else:
            # Use the default beautifully formatted interview invitation template
            background_tasks.add_task(
                email_service.send_interview_scheduled_email,
                app["email"], app["name"], app["job_title"],
                data.date_time, data.meeting_link, data.interviewer
            )

    return {"message": "Interview scheduled successfully", "interview": interview_doc}

@router.get("")
async def list_interviews(current_user: dict = Depends(get_current_user)):
    """
    Returns all interviews created by the logged-in recruiter.
    Only shows interviews that belong to this specific recruiter (isolation by user).
    """
    cursor = interviews_collection.find({"created_by": current_user["user_id"]})
    interviews = await cursor.to_list(length=200)  # Load up to 200 interviews at most
    return {"interviews": interviews, "total": len(interviews)}

@router.patch("/{interview_id}/status")
async def update_interview_status(
    interview_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Updates the status of a scheduled interview.
    
    Allowed statuses:
    - "scheduled"  — Interview is upcoming (default after scheduling)
    - "completed"  — The interview took place
    - "cancelled"  — The interview was cancelled
    """
    new_status = body.get("status")
    # Validate the status is one of the three allowed values
    if new_status not in ["scheduled", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    # Ensure the interview belongs to this recruiter before allowing updates
    interview = await interviews_collection.find_one({"_id": interview_id, "created_by": current_user["user_id"]})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    # Perform the status update in MongoDB
    await interviews_collection.update_one({"_id": interview_id}, {"$set": {"status": new_status}})
    return {"message": f"Interview status updated to {new_status}"}
