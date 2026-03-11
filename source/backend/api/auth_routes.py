from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.api.schemas import LoginRequest, LoginResponse
from backend.database.mongodb import get_db
from backend.utils.jwt_handler import create_access_token
from backend.utils.security import verify_password


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)) -> LoginResponse:
    # doctors and admins share the same login endpoint
    admin = await db["admin"].find_one({"email": payload.email})
    if admin and verify_password(payload.password, admin["password_hash"]):
        token = create_access_token(subject=payload.email, role="admin")
        return LoginResponse(access_token=token, role="admin")

    doctor = await db["doctor"].find_one({"email": payload.email})
    if doctor and verify_password(payload.password, doctor["password_hash"]):
        token = create_access_token(subject=payload.email, role="doctor")
        return LoginResponse(access_token=token, role="doctor")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

