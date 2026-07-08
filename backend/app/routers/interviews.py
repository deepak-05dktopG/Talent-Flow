from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.schemas import InterviewCreate
from app.database import interviews_collection, applications_collection
from app.utils.auth import get_current_user
from app.services import email_service
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/interviews", tags=["interviews"])

@router.post("", status_code=201)
async def schedule_interview(
    data: InterviewCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    app = await applications_collection.find_one({"_id": data.application_id, "created_by": current_user["user_id"]})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    interview_doc = {
        "_id": str(uuid.uuid4()),
        "candidate_id": app["_id"],
        "application_id": data.application_id,
        "job_id": app["job_id"],
        "job_title": app["job_title"],
        "candidate_name": app["name"],
        "candidate_email": app["email"],
        "date_time": data.date_time,
        "meeting_link": data.meeting_link,
        "interviewer": data.interviewer,
        "status": "scheduled",
        "created_by": current_user["user_id"],
        "created_at": datetime.utcnow().isoformat()
    }
    await interviews_collection.insert_one(interview_doc)

    # Update application status
    await applications_collection.update_one(
        {"_id": data.application_id},
        {"$set": {"status": "interview_scheduled"}}
    )

    # Send email notification
    if data.send_email:
        if data.email_body:
            background_tasks.add_task(
                email_service.send_custom_body_email,
                app["email"],
                f"Interview Scheduled: {app['job_title']}",
                data.email_body
            )
        else:
            background_tasks.add_task(
                email_service.send_interview_scheduled_email,
                app["email"], app["name"], app["job_title"],
                data.date_time, data.meeting_link, data.interviewer
            )

    return {"message": "Interview scheduled successfully", "interview": interview_doc}

@router.get("")
async def list_interviews(current_user: dict = Depends(get_current_user)):
    cursor = interviews_collection.find({"created_by": current_user["user_id"]})
    interviews = await cursor.to_list(length=200)
    return {"interviews": interviews, "total": len(interviews)}

@router.patch("/{interview_id}/status")
async def update_interview_status(
    interview_id: str,
    body: dict,
    current_user: dict = Depends(get_current_user)
):
    new_status = body.get("status")
    if new_status not in ["scheduled", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    interview = await interviews_collection.find_one({"_id": interview_id, "created_by": current_user["user_id"]})
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    await interviews_collection.update_one({"_id": interview_id}, {"$set": {"status": new_status}})
    return {"message": f"Interview status updated to {new_status}"}
