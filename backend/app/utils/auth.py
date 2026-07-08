"""
utils/auth.py - Authentication & Security Utilities
=====================================================
This file provides the building blocks for securing the application.
It handles three main security tasks:
  1. Password hashing — converts plain passwords into secure, unreadable hashes
  2. JWT token creation — generates login tokens when a recruiter signs in
  3. Token verification — checks login tokens on every protected API request

Think of JWT tokens like hotel key cards: after you check in (login), you get a
card (token) that lets you access your room (API endpoints) without showing your
password every time. The card expires after a set time (ACCESS_TOKEN_EXPIRE_MINUTES).
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app import config

# HTTPBearer reads the "Authorization: Bearer <token>" header from incoming requests
security = HTTPBearer()

def hash_password(password: str) -> str:
    """
    Converts a plain-text password into a secure, scrambled hash.
    
    How it works:
    - The password is encoded to bytes
    - A unique random "salt" is generated (adds randomness to prevent identical hashes)
    - bcrypt scrambles the password + salt together into an unreadable string
    - This hash is stored in the database — the original password is NEVER stored
    
    Example: "mypassword123" → "$2b$12$xH7jK...randomhash...xPqW"
    """
    pwd_bytes = password.encode('utf-8')      # Convert string to bytes
    salt = bcrypt.gensalt()                   # Generate a unique random salt
    hashed = bcrypt.hashpw(pwd_bytes, salt)   # Hash the password with the salt
    return hashed.decode('utf-8')             # Convert back to string for storage

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain-text password matches the stored hash during login.
    
    Returns True if the password is correct, False otherwise.
    bcrypt handles this securely — it re-applies the same hashing logic
    and compares results without ever having to "unhash" the stored password.
    """
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False  # If any error occurs, deny access for safety

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT login token that contains the user's identity.
    
    How it works:
    - Takes user data (like user_id and email) as input
    - Adds an expiry time when the token will stop working
    - Encodes everything into a compact signed string using the JWT_SECRET key
    - This token is sent to the frontend after login and sent back with every request
    
    Example output: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    to_encode = data.copy()
    # Set the expiry time — defaults to ACCESS_TOKEN_EXPIRE_MINUTES from config
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})  # Add the expiry timestamp to the token payload
    # Sign and encode the token using our secret key
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """
    Decodes a JWT token and returns the user data inside it.
    
    Returns an empty dict if:
    - The token is expired
    - The token has been tampered with
    - The token is invalid or malformed
    """
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return payload  # Returns the original data dict that was encoded into the token
    except JWTError:
        return {}  # Invalid or expired token

# Optional bearer security — doesn't auto-reject missing tokens (we handle that manually)
security_optional = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    token: Optional[str] = Query(None)  # Also accepts token as a URL query parameter
):
    """
    A FastAPI "dependency" that protects any endpoint requiring the user to be logged in.
    
    When added to an endpoint with Depends(get_current_user), FastAPI will:
    1. Extract the JWT token from the Authorization header or URL query string
    2. Decode and validate the token
    3. Return the logged-in user's identity (user_id, email, company_name)
    4. Or raise a 401 Unauthorized error if the token is missing or invalid
    
    This function is used on every protected route — it's the "security guard" of the API.
    """
    actual_token = None

    # Check the Authorization header first (most common method)
    if credentials:
        actual_token = credentials.credentials
    # Fall back to checking a token passed as a URL parameter (used for file preview links)
    elif token:
        actual_token = token

    # If no token is found at all, reject the request
    if not actual_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode the token to get the user's identity
    payload = decode_token(actual_token)
    user_id = payload.get("user_id")

    # If the token is invalid or expired, user_id will be None — reject the request
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return the logged-in user's data to the calling endpoint
    return {"user_id": user_id, "email": payload.get("email"), "company_name": payload.get("company_name")}
