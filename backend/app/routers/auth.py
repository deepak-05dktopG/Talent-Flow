"""
routers/auth.py - Authentication API Endpoints
================================================
This file handles all login-related API routes.

Endpoints:
  POST /api/auth/register  — Create a new HR recruiter account
  POST /api/auth/login     — Log in and receive a JWT token
  GET  /api/auth/me        — Simple check to verify auth is working

How login works:
1. Recruiter sends email + password to /api/auth/login
2. We look up the user in MongoDB by email
3. We verify the password against the stored hash using bcrypt
4. If correct, we generate a JWT token and send it back
5. The frontend stores this token and sends it with every future request
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas import UserRegister, UserLogin, Token
from app.database import users_collection
from app.utils.auth import hash_password, verify_password, create_access_token
from datetime import datetime
import uuid

# All routes in this file are prefixed with /api/auth
router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Creates a new HR recruiter account.
    
    Steps:
    1. Check if the email is already registered — if yes, reject with a 400 error
    2. Hash the password securely using bcrypt before storing
    3. Create a new user document in the 'users' MongoDB collection
    4. Generate and return a JWT login token immediately (so the user is auto-logged in)
    """
    # Prevent duplicate accounts for the same email address
    existing = await users_collection.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Build the user record to save in MongoDB
    user_doc = {
        "_id": str(uuid.uuid4()),      # Generate a unique ID for this user
        "email": user_data.email,
        "password": hash_password(user_data.password),  # Never store plain passwords!
        "company_name": user_data.company_name,
        "phone": user_data.phone,
        "role": "hr",                  # Default role is HR recruiter
        "created_at": datetime.utcnow().isoformat()  # Timestamp of account creation
    }
    await users_collection.insert_one(user_doc)  # Save to MongoDB

    # Auto-login: generate a JWT token and return it so the user doesn't need to log in again
    token = create_access_token({"user_id": user_doc["_id"], "email": user_doc["email"], "company_name": user_doc["company_name"]})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Authenticates an existing HR recruiter and returns a JWT token.
    
    Steps:
    1. Look up the user by email in MongoDB
    2. Use bcrypt to verify the provided password matches the stored hash
    3. If valid, generate a JWT token with the user's identity embedded
    4. Return the token — the frontend stores this in localStorage
    
    Returns a 401 error if the email doesn't exist or the password is wrong.
    """
    # Look up the user account by email address
    user = await users_collection.find_one({"email": credentials.email})
    # Reject if user doesn't exist OR if the password doesn't match
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Password matched — generate a login token containing the user's identity
    token = create_access_token({"user_id": user["_id"], "email": user["email"], "company_name": user["company_name"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: dict = None):
    """
    Simple sanity check endpoint to verify authentication is working.
    Returns a basic confirmation message.
    Visit: GET /api/auth/me
    """
    return {"message": "Auth is working"}
