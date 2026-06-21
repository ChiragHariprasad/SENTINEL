import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.auth import hash_password
from app.models.user import User, Role
from app.schemas.user import UserResponse, UserCreate, UserUpdate, RoleResponse
from app.schemas.common import StandardResponse
from app.core.exceptions import NotFoundError, DuplicateError

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def list_users(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return StandardResponse(data={"items": [UserResponse.model_validate(u).model_dump() for u in users]})


@router.post("")
async def create_user(request: UserCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        raise DuplicateError("A user with this email already exists")
    return StandardResponse(data=UserResponse.model_validate(user).model_dump())


@router.get("/{user_id}")
async def get_user(user_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User", str(user_id))
    return StandardResponse(data=UserResponse.model_validate(user).model_dump())


@router.put("/{user_id}")
async def update_user(user_id: uuid.UUID, request: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User", str(user_id))

    if request.first_name is not None:
        user.first_name = request.first_name
    if request.last_name is not None:
        user.last_name = request.last_name
    if request.role is not None:
        user.role = request.role
    if request.is_active is not None:
        user.is_active = request.is_active

    await db.flush()
    return StandardResponse(data=UserResponse.model_validate(user).model_dump())


@router.get("/roles/list")
async def list_roles(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return StandardResponse(data={"items": [RoleResponse.model_validate(r).model_dump() for r in roles]})
