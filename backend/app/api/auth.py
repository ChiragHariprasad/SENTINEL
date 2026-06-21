from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, RefreshRequest
from app.schemas.common import StandardResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup")
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token({"sub": str(user.user_id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.user_id)})

    return StandardResponse(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 900,
        "role": user.role,
    })


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.user_id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.user_id)})

    return StandardResponse(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 900,
        "role": user.role,
    })


@router.post("/refresh")
async def refresh(request: RefreshRequest):
    payload = decode_token(request.refresh_token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    return StandardResponse(data={
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 900,
    })


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return StandardResponse(message="Logged out successfully")
