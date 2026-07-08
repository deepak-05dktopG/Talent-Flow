"""
services/storage_service.py - File Upload & Storage Service
=============================================================
This file handles uploading candidate resume PDF files to cloud storage (Cloudinary).

How it works:
- When a candidate applies for a job, their PDF resume is sent to this service.
- If Cloudinary is configured: the file is uploaded to the cloud and a permanent URL is returned.
- If Cloudinary is NOT configured: the file is saved to a local folder called "uploads/"
  and a local API URL is returned instead.

Cloudinary is a media hosting platform — it stores files safely in the cloud
and gives each file a public-accessible HTTPS URL (e.g., https://res.cloudinary.com/...).
"""

import os
import uuid
import cloudinary
import cloudinary.uploader
from app import config

# ──────────────────────────────────────────────
# CLOUDINARY SETUP
# ──────────────────────────────────────────────
# Check if all three Cloudinary credentials are present in the .env file
if config.CLOUDINARY_CLOUD_NAME and config.CLOUDINARY_API_KEY and config.CLOUDINARY_API_SECRET:
    # Configure the Cloudinary library with credentials from .env
    cloudinary.config(
        cloud_name=config.CLOUDINARY_CLOUD_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET
    )
    USE_CLOUDINARY = True   # Cloud storage enabled
else:
    USE_CLOUDINARY = False  # Fall back to local folder storage
    # Ensure the local uploads folder exists before saving any files
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)

def upload_resume(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """
    Uploads a resume file and returns its accessible URL.
    
    Parameters:
        file_bytes   - The raw binary content of the uploaded PDF
        filename     - Original file name (e.g., "john_cv.pdf")
        content_type - MIME type (e.g., "application/pdf")
    
    Returns a dict with:
        - 'url': The full URL where the resume can be viewed/downloaded
        - 'local_path': The local file path (None if using Cloudinary)
    """
    # Extract the file extension (e.g., ".pdf") from the original filename
    _, ext = os.path.splitext(filename)
    # Generate a unique random filename to prevent collisions/overwriting
    unique_name = f"resume_{uuid.uuid4().hex}{ext}"

    if USE_CLOUDINARY:
        try:
            # Upload the file to Cloudinary under the "talentflow/resumes/" folder
            result = cloudinary.uploader.upload(
                file_bytes,
                public_id=f"talentflow/resumes/{unique_name}",
                resource_type="auto"  # Auto-detects PDF, image, etc.
            )
            # Return the secure HTTPS URL that Cloudinary provides
            return {"url": result.get("secure_url", ""), "local_path": None}
        except Exception as e:
            # If Cloudinary upload fails (network issue, etc.), warn and fall back to local
            print(f"[Storage] Cloudinary upload failed: {e}. Falling back to local storage.")

    # Fallback: save the file to the local "uploads/" directory
    local_path = os.path.join(config.UPLOAD_DIR, unique_name)
    with open(local_path, "wb") as f:
        f.write(file_bytes)
    # Return a relative API URL — the backend serves this file directly via /api/resumes/
    url = f"/api/resumes/{unique_name}"
    return {"url": url, "local_path": local_path}
