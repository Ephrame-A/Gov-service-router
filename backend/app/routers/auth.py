"""Authentication endpoints — login and register."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, get_current_user, hash_password, require_roles, verify_password
from app.db.models import Institution, User
from app.db.session import get_db
from app.schemas import AuthResponse, LoginRequest, OfficerResponse, PasswordChangeRequest, RegisterRequest, UserResponse

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


@router.post("/auth/register", response_model=OfficerResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    existing = await db.execute(select(User).where(User.email == request.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    try:
        institution_id = uuid.UUID(request.institution_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid institution_id")

    inst = await db.execute(select(Institution).where(Institution.id == institution_id))
    institution = inst.scalar_one_or_none()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    if not institution.is_approved:
        raise HTTPException(status_code=400, detail="Approve the institution before adding officers")

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role="officer",
        institution_id=institution_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return OfficerResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        institution_id=str(user.institution_id),
        institution_name=institution.name,
    )


@router.get("/auth/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        institution_id=str(user.institution_id) if user.institution_id else None,
    )


@router.post("/auth/change-password", status_code=204)
async def change_password(
    request: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(request.new_password)
    await db.commit()
