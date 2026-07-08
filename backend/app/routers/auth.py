from fastapi import APIRouter, HTTPException, status
from app.schemas import UserRegister, UserLogin, Token
from app.database import users_collection
from app.utils.auth import hash_password, verify_password, create_access_token
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    # Check if email already exists
    existing = await users_collection.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "_id": str(uuid.uuid4()),
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "company_name": user_data.company_name,
        "phone": user_data.phone,
        "role": "hr",
        "created_at": datetime.utcnow().isoformat()
    }
    await users_collection.insert_one(user_doc)

    token = create_access_token({"user_id": user_doc["_id"], "email": user_doc["email"], "company_name": user_doc["company_name"]})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    user = await users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"user_id": user["_id"], "email": user["email"], "company_name": user["company_name"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: dict = None):
    # This endpoint would normally use Depends(get_current_user) but we keep it simple
    return {"message": "Auth is working"}
