"""Admin endpoints — institution approval queue."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_roles
from app.db.models import Institution, User
from app.db.session import get_db
from app.schemas import InstitutionResponse

router = APIRouter()


@router.get("/admin/pending-institutions", response_model=list[InstitutionResponse])
async def list_pending_institutions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    result = await db.execute(
        select(Institution)
        .where(Institution.is_approved.is_(False))
        .order_by(Institution.created_at.desc())
    )
    return [
        InstitutionResponse(
            id=str(i.id),
            name=i.name,
            type=i.type,
            description=i.description,
            is_approved=i.is_approved,
            created_at=i.created_at.isoformat(),
        )
        for i in result.scalars().all()
    ]


@router.post("/admin/institutions/{institution_id}/approve", response_model=InstitutionResponse)
async def approve_institution(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    import uuid

    result = await db.execute(
        select(Institution).where(Institution.id == uuid.UUID(institution_id))
    )
    institution = result.scalar_one_or_none()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    institution.is_approved = True
    await db.commit()
    await db.refresh(institution)
    return InstitutionResponse(
        id=str(institution.id),
        name=institution.name,
        type=institution.type,
        description=institution.description,
        is_approved=institution.is_approved,
        created_at=institution.created_at.isoformat(),
    )


@router.post("/admin/institutions/{institution_id}/reject", status_code=204)
async def reject_institution(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    import uuid

    result = await db.execute(
        select(Institution).where(Institution.id == uuid.UUID(institution_id))
    )
    institution = result.scalar_one_or_none()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    await db.delete(institution)
    await db.commit()
