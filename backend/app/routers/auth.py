"""Authentication endpoints — login and register."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.db.models import Institution, User
from app.db.session import get_db
from app.schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse

router = APIRouter()


@router.post("/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(
        str(user.id), user.role, str(user.institution_id) if user.institution_id else None
    )
    return AuthResponse(
        access_token=token,
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        institution_id=str(user.institution_id) if user.institution_id else None,
    )


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    institution_id = None
    if request.institution_id:
        try:
            institution_id = uuid.UUID(request.institution_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid institution_id")

        inst = await db.execute(select(Institution).where(Institution.id == institution_id))
        if not inst.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Institution not found")

    if request.role == "officer" and not institution_id:
        raise HTTPException(status_code=400, detail="Officers must be linked to an institution")

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
        institution_id=institution_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(
        str(user.id), user.role, str(user.institution_id) if user.institution_id else None
    )
    return AuthResponse(
        access_token=token,
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        institution_id=str(user.institution_id) if user.institution_id else None,
    )


@router.get("/auth/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        institution_id=str(user.institution_id) if user.institution_id else None,
    )
