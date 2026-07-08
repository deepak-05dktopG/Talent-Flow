"""
routers/analytics.py - Dashboard Analytics API Endpoint
=========================================================
This file provides a single endpoint that powers the Analytics dashboard in the frontend.
It computes and returns all the numbers, charts, and statistics that HR managers see
on their main dashboard when they log in.

Endpoint:
  GET /api/analytics  — Returns KPIs, charts, and funnel data for the logged-in recruiter

What data is returned:
  - KPIs (Key Performance Indicators): Total jobs, total applicants, hired count, etc.
  - Applications Per Job: A bar chart showing how many people applied for each job posting
  - Top Skills: The most common skills seen across all candidates' resumes
  - Applications By Month: A line chart showing application volume over the last 6 months
  - Hiring Funnel: How many candidates are at each stage (Applied → Shortlisted → Hired)

Data isolation:
  Every query is filtered by the logged-in recruiter's user ID, so each recruiter
  only sees analytics for their own jobs and candidates.
"""

from fastapi import APIRouter, Depends
from app.database import jobs_collection, applications_collection, interviews_collection
from app.utils.auth import get_current_user

# All routes prefixed with /api/analytics
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    """
    Fetches all analytics data for the logged-in HR recruiter's dashboard.
    
    Queries MongoDB for counts and lists across jobs and applications,
    then processes and returns all data in a single structured response.
    """
    uid = current_user["user_id"]  # The recruiter's unique ID — used to filter all queries

    # ──────────────────────────────────────────────
    # JOB COUNTS
    # ──────────────────────────────────────────────
    total_jobs = await jobs_collection.count_documents({"created_by": uid})         # All jobs ever created
    active_jobs = await jobs_collection.count_documents({"created_by": uid, "is_active": True})  # Currently open jobs

    # ──────────────────────────────────────────────
    # APPLICATION STATUS COUNTS
    # Count how many candidates are at each stage of the funnel
    # ──────────────────────────────────────────────
    total_apps = await applications_collection.count_documents({"created_by": uid})
    shortlisted = await applications_collection.count_documents({"created_by": uid, "status": "shortlisted"})
    rejected = await applications_collection.count_documents({"created_by": uid, "status": "rejected"})
    interviews_sched = await applications_collection.count_documents({"created_by": uid, "status": "interview_scheduled"})
    offered = await applications_collection.count_documents({"created_by": uid, "status": "offered"})
    hired = await applications_collection.count_documents({"created_by": uid, "status": "hired"})

    # ──────────────────────────────────────────────
    # APPLICATIONS PER JOB (for bar chart)
    # ──────────────────────────────────────────────
    # Load all the recruiter's jobs, then count applications for each one
    cursor = jobs_collection.find({"created_by": uid})
    all_jobs = await cursor.to_list(length=200)
    apps_per_job = []
    for job in all_jobs:
        count = await applications_collection.count_documents({"created_by": uid, "job_id": job["_id"]})
        apps_per_job.append({"job_title": job["title"], "count": count})

    # ──────────────────────────────────────────────
    # TOP SKILLS ACROSS ALL APPLICANTS (for pie/bar chart)
    # ──────────────────────────────────────────────
    # Load all applications and tally up how many times each skill appears
    cursor = applications_collection.find({"created_by": uid})
    all_apps = await cursor.to_list(length=500)
    skill_count = {}
    for app in all_apps:
        for skill in app.get("parsed_skills", []):
            skill_count[skill] = skill_count.get(skill, 0) + 1
    # Sort by frequency and take the top 10 most common skills
    top_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)[:10]
    top_skills_list = [{"skill": s, "count": c} for s, c in top_skills]

    # ──────────────────────────────────────────────
    # AVERAGE MATCH SCORE
    # ──────────────────────────────────────────────
    # Compute the average AI match score across all applications
    scores = [a.get("match_score", 0) for a in all_apps]
    avg_score = round(sum(scores) / max(len(scores), 1), 1)  # Avoid division by zero with max(..., 1)

    # ──────────────────────────────────────────────
    # APPLICATIONS BY MONTH (for trend line chart)
    # ──────────────────────────────────────────────
    from collections import defaultdict
    monthly = defaultdict(int)
    for app in all_apps:
        applied_at = app.get("applied_at", "")
        if applied_at:
            month_key = applied_at[:7]  # Extract "YYYY-MM" from the full timestamp string
            monthly[month_key] += 1
    # Sort chronologically and return only the last 6 months
    apps_by_month = sorted([{"month": k, "count": v} for k, v in monthly.items()])[-6:]

    # ──────────────────────────────────────────────
    # RETURN ALL ANALYTICS DATA
    # ──────────────────────────────────────────────
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
        "apps_per_job": apps_per_job,         # Bar chart: applications per job posting
        "top_skills": top_skills_list,         # Bar/pie chart: most common candidate skills
        "apps_by_month": apps_by_month,        # Line chart: application volume over time
        "hiring_funnel": [                     # Funnel chart: candidate progression stages
            {"stage": "Applied", "count": total_apps},
            {"stage": "Shortlisted", "count": shortlisted},
            {"stage": "Interviewed", "count": interviews_sched},
            {"stage": "Offered", "count": offered},
            {"stage": "Hired", "count": hired},
        ]
    }
