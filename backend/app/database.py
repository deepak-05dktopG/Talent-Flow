"""
database.py - Database Connection & Collection Setup
=====================================================
This file connects our application to the MongoDB cloud database.
MongoDB stores all of TalentFlow's data: users, jobs, candidates, interviews, etc.

Each "collection" is like a table in a spreadsheet — it holds a specific type of data.
For example, the "jobs" collection stores all job postings, and the "applications" 
collection stores all candidate applications.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app import config

# ──────────────────────────────────────────────
# CONNECT TO MONGODB
# ──────────────────────────────────────────────
# Create a connection to MongoDB Atlas (cloud database).
# 'tlsAllowInvalidCertificates=True' helps avoid SSL certificate errors on some networks.
client = AsyncIOMotorClient(config.MONGO_URI, tlsAllowInvalidCertificates=True)

# Select our specific database from the MongoDB server
db = client[config.DB_NAME]

print("--- SERVICE STATUS LOG ---")
print("MongoDB: AsyncIOMotorClient initialized (tlsAllowInvalidCertificates=True)")

# ──────────────────────────────────────────────
# DATABASE COLLECTIONS (like tables in a spreadsheet)
# ──────────────────────────────────────────────

# Stores recruiter/HR user accounts (email, password hash, company name)
users_collection = db["users"]

# Stores company profiles
companies_collection = db["companies"]

# Stores all job postings created by recruiters (title, description, requirements, hiring rounds)
jobs_collection = db["jobs"]

# Stores individual candidate profiles
candidates_collection = db["candidates"]

# Stores job applications submitted by candidates (resume, parsed skills, match score, status)
applications_collection = db["applications"]

# Stores scheduled interview records (date, time, meeting link, interviewer)
interviews_collection = db["interviews"]

# Stores notification logs
notifications_collection = db["notifications"]
