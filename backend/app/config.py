"""
config.py - Application Configuration File
============================================
This file loads all secret keys, database credentials, and service settings
from the .env file. Think of it as the "settings page" for the entire backend.
Every external service (database, email, AI, file storage) is configured here.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file into the system
load_dotenv()

# ──────────────────────────────────────────────
# APPLICATION SETTINGS
# ──────────────────────────────────────────────
# The name of our application and which port the server runs on
APP_NAME = "TalentFlow API"
PORT = int(os.getenv("PORT", 8000))

# ──────────────────────────────────────────────
# SECURITY / LOGIN SETTINGS (JWT)
# ──────────────────────────────────────────────
# JWT (JSON Web Token) is how we verify that a logged-in recruiter is who they say they are.
# JWT_SECRET is the private key used to sign login tokens — keep this secret!
# JWT_ALGORITHM is the encryption method (HS256 is a standard, secure choice).
# ACCESS_TOKEN_EXPIRE_MINUTES controls how long a recruiter stays logged in before needing to re-login.
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-for-talentflow-auth-token-generation-2026")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# ──────────────────────────────────────────────
# DATABASE SETTINGS (MongoDB)
# ──────────────────────────────────────────────
# MONGO_URI is the connection string to our cloud MongoDB database where all data lives.
# DB_NAME is the specific database name inside MongoDB (like a folder name).
# MOCK_DB_FILE is a fallback local file used if MongoDB is not available (for offline testing).
MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "talentflow")
MOCK_DB_FILE = os.getenv("MOCK_DB_FILE", "talentflow_local_db.json")

# ──────────────────────────────────────────────
# AI SERVICE SETTINGS (Groq / Llama 3)
# ──────────────────────────────────────────────
# GROQ_API_KEY is the secret key to access Groq's AI model (Llama 3).
# This AI reads candidate resumes and extracts skills, experience, and match scores.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ──────────────────────────────────────────────
# EMAIL SETTINGS (SMTP / Gmail)
# ──────────────────────────────────────────────
# These settings allow the app to send real emails to candidates.
# SMTP_HOST: The email server address (Gmail's is smtp.gmail.com)
# SMTP_PORT: The port number for the email server (587 is standard for Gmail)
# SMTP_USER: Your Gmail address (e.g., hr@company.com)
# SMTP_PASSWORD: A 16-character App Password generated from your Google Account security settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ──────────────────────────────────────────────
# FILE STORAGE SETTINGS (Cloudinary)
# ──────────────────────────────────────────────
# Cloudinary is a cloud service that stores uploaded resume PDF files.
# When a candidate applies, their resume is uploaded to Cloudinary and a URL is returned.
# UPLOAD_DIR is the local fallback folder if Cloudinary is not configured.
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# ──────────────────────────────────────────────
# STARTUP HEALTH CHECK
# ──────────────────────────────────────────────
def print_service_statuses():
    """
    Prints a summary of which services are properly configured when the server starts.
    This helps developers quickly see if any credentials are missing.
    """
    print("--- SERVICE STATUS LOG ---")
    print(f"MongoDB: {'Connected to Atlas' if MONGO_URI else 'FALLBACK (Using Local JSON DB)'}")
    print(f"Groq API: {'Configured' if GROQ_API_KEY else 'FALLBACK (Using Heuristic AI Parser)'}")
    print(f"SMTP Email: {'Configured' if SMTP_USER and SMTP_PASSWORD else 'FALLBACK (Using Local Email Console Log)'}")
    print(f"Cloudinary: {'Configured' if CLOUDINARY_CLOUD_NAME else 'FALLBACK (Using Local Folder Storage)'}")
    print("--------------------------")
