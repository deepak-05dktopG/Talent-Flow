import os
from dotenv import load_dotenv

load_dotenv()

# App Configurations
APP_NAME = "TalentFlow API"
PORT = int(os.getenv("PORT", 8000))

# JWT Configurations
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-for-talentflow-auth-token-generation-2026")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# Database Configuration
MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "talentflow")
MOCK_DB_FILE = os.getenv("MOCK_DB_FILE", "talentflow_local_db.json")

# Third-party APIs
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# SMTP Mail configurations
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Cloudinary Storage Configurations
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# Dynamic Fallback Logging
def print_service_statuses():
    print("--- SERVICE STATUS LOG ---")
    print(f"MongoDB: {'Connected to Atlas' if MONGO_URI else 'FALLBACK (Using Local JSON DB)'}")
    print(f"Groq API: {'Configured' if GROQ_API_KEY else 'FALLBACK (Using Heuristic AI Parser)'}")
    print(f"SMTP Email: {'Configured' if SMTP_USER and SMTP_PASSWORD else 'FALLBACK (Using Local Email Console Log)'}")
    print(f"Cloudinary: {'Configured' if CLOUDINARY_CLOUD_NAME else 'FALLBACK (Using Local Folder Storage)'}")
    print("--------------------------")
