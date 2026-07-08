import os
import uuid
import cloudinary
import cloudinary.uploader
from app import config

# Configure Cloudinary if credentials are present
if config.CLOUDINARY_CLOUD_NAME and config.CLOUDINARY_API_KEY and config.CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=config.CLOUDINARY_CLOUD_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET
    )
    USE_CLOUDINARY = True
else:
    USE_CLOUDINARY = False
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)

def upload_resume(file_bytes: bytes, filename: str, content_type: str) -> dict:
    """Upload a resume file and return {'url': ..., 'local_path': ...}"""
    _, ext = os.path.splitext(filename)
    unique_name = f"resume_{uuid.uuid4().hex}{ext}"

    if USE_CLOUDINARY:
        try:
            result = cloudinary.uploader.upload(
                file_bytes,
                public_id=f"talentflow/resumes/{unique_name}",
                resource_type="auto"
            )
            return {"url": result.get("secure_url", ""), "local_path": None}
        except Exception as e:
            print(f"[Storage] Cloudinary upload failed: {e}. Falling back to local storage.")

    # Fallback: save locally
    local_path = os.path.join(config.UPLOAD_DIR, unique_name)
    with open(local_path, "wb") as f:
        f.write(file_bytes)
    # Return a pseudo-URL pointing to the API serve endpoint
    url = f"/api/resumes/{unique_name}"
    return {"url": url, "local_path": local_path}
