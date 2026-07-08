from fastapi import APIRouter, Depends
from app.database import jobs_collection, applications_collection, interviews_collection
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    uid = current_user["user_id"]

    # Jobs counts
    total_jobs = await jobs_collection.count_documents({"created_by": uid})
    active_jobs = await jobs_collection.count_documents({"created_by": uid, "is_active": True})

    # Applications counts
    total_apps = await applications_collection.count_documents({"created_by": uid})
    shortlisted = await applications_collection.count_documents({"created_by": uid, "status": "shortlisted"})
    rejected = await applications_collection.count_documents({"created_by": uid, "status": "rejected"})
    interviews_sched = await applications_collection.count_documents({"created_by": uid, "status": "interview_scheduled"})
    offered = await applications_collection.count_documents({"created_by": uid, "status": "offered"})
    hired = await applications_collection.count_documents({"created_by": uid, "status": "hired"})

    # Applications per job
    cursor = jobs_collection.find({"created_by": uid})
    all_jobs = await cursor.to_list(length=200)
    apps_per_job = []
    for job in all_jobs:
        count = await applications_collection.count_documents({"created_by": uid, "job_id": job["_id"]})
        apps_per_job.append({"job_title": job["title"], "count": count})

    # Top Skills distribution among applicants
    cursor = applications_collection.find({"created_by": uid})
    all_apps = await cursor.to_list(length=500)
    skill_count = {}
    for app in all_apps:
        for skill in app.get("parsed_skills", []):
            skill_count[skill] = skill_count.get(skill, 0) + 1
    top_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:10]
    top_skills_list = [{"skill": s, "count": c} for s, c in top_skills]

    # Avg match score
    scores = [a.get("match_score", 0) for a in all_apps]
    avg_score = round(sum(scores) / max(len(scores), 1), 1)

    # Applications by month (last 6 months)
    from collections import defaultdict
    monthly = defaultdict(int)
    for app in all_apps:
        applied_at = app.get("applied_at", "")
        if applied_at:
            month_key = applied_at[:7]  # YYYY-MM
            monthly[month_key] += 1
    apps_by_month = sorted([{"month": k, "count": v} for k, v in monthly.items()])[-6:]

    return {
        "kpis": {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applicants": total_apps,
            "shortlisted": shortlisted,
            "rejected": rejected,
            "interviews_scheduled": interviews_sched,
            "offers_sent": offered,
            "hired": hired,
            "avg_match_score": avg_score
        },
        "apps_per_job": apps_per_job,
        "top_skills": top_skills_list,
        "apps_by_month": apps_by_month,
        "hiring_funnel": [
            {"stage": "Applied", "count": total_apps},
            {"stage": "Shortlisted", "count": shortlisted},
            {"stage": "Interviewed", "count": interviews_sched},
            {"stage": "Offered", "count": offered},
            {"stage": "Hired", "count": hired},
        ]
    }
