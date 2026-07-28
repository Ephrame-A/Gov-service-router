"""Institution, department, and service CRUD — officer-authenticated."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_roles
from app.db.models import Department, Institution, Service, User
from app.db.session import get_db
from app.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    InstitutionCreate,
    InstitutionResponse,
    InstitutionUpdate,
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)

router = APIRouter()


def _institution_response(inst: Institution) -> InstitutionResponse:
    return InstitutionResponse(
        id=str(inst.id),
        name=inst.name,
        type=inst.type,
        description=inst.description,
        is_approved=inst.is_approved,
        created_at=inst.created_at.isoformat(),
    )


def _department_response(dept: Department) -> DepartmentResponse:
    return DepartmentResponse(
        id=str(dept.id),
        institution_id=str(dept.institution_id),
        name=dept.name,
        description=dept.description,
    )


def _service_response(svc: Service) -> ServiceResponse:
    return ServiceResponse(
        id=str(svc.id),
        department_id=str(svc.department_id),
        office_id=str(svc.office_id) if svc.office_id else None,
        name=svc.name,
        description=svc.description,
        example_phrasings=svc.example_phrasings or [],
        required_documents=svc.required_documents or [],
        typical_duration=svc.typical_duration,
        fees=svc.fees,
        has_embedding=svc.embedding is not None,
    )


async def _check_institution_access(
    institution_id: uuid.UUID, user: User, db: AsyncSession
) -> Institution:
    result = await db.execute(select(Institution).where(Institution.id == institution_id))
    institution = result.scalar_one_or_none()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    if user.role == "officer" and user.institution_id != institution_id:
        raise HTTPException(status_code=403, detail="Cannot access another institution")
    return institution


# --- Institutions ---


@router.get("/institutions", response_model=list[InstitutionResponse])
async def list_institutions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    if user.role == "officer":
        result = await db.execute(
            select(Institution).where(Institution.id == user.institution_id)
        )
    else:
        result = await db.execute(select(Institution).order_by(Institution.name))
    return [_institution_response(i) for i in result.scalars().all()]


@router.post("/institutions", response_model=InstitutionResponse, status_code=201)
async def create_institution(
    body: InstitutionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    institution = Institution(
        name=body.name,
        type=body.type,
        description=body.description,
        is_approved=user.role == "admin",
    )
    db.add(institution)
    await db.commit()
    await db.refresh(institution)
    return _institution_response(institution)


@router.get("/institutions/{institution_id}", response_model=InstitutionResponse)
async def get_institution(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    inst = await _check_institution_access(uuid.UUID(institution_id), user, db)
    return _institution_response(inst)


@router.put("/institutions/{institution_id}", response_model=InstitutionResponse)
async def update_institution(
    institution_id: str,
    body: InstitutionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    inst = await _check_institution_access(uuid.UUID(institution_id), user, db)
    if body.name is not None:
        inst.name = body.name
    if body.type is not None:
        inst.type = body.type
    if body.description is not None:
        inst.description = body.description
    await db.commit()
    await db.refresh(inst)
    return _institution_response(inst)


@router.delete("/institutions/{institution_id}", status_code=204)
async def delete_institution(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    inst = await _check_institution_access(uuid.UUID(institution_id), user, db)
    await db.delete(inst)
    await db.commit()


# --- Departments ---


@router.get("/institutions/{institution_id}/departments", response_model=list[DepartmentResponse])
async def list_departments(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    inst_id = uuid.UUID(institution_id)
    await _check_institution_access(inst_id, user, db)
    result = await db.execute(
        select(Department).where(Department.institution_id == inst_id)
    )
    return [_department_response(d) for d in result.scalars().all()]


@router.post(
    "/institutions/{institution_id}/departments",
    response_model=DepartmentResponse,
    status_code=201,
)
async def create_department(
    institution_id: str,
    body: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    inst_id = uuid.UUID(institution_id)
    await _check_institution_access(inst_id, user, db)
    dept = Department(institution_id=inst_id, name=body.name, description=body.description)
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return _department_response(dept)


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    body: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    result = await db.execute(select(Department).where(Department.id == uuid.UUID(department_id)))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    await _check_institution_access(dept.institution_id, user, db)
    if body.name is not None:
        dept.name = body.name
    if body.description is not None:
        dept.description = body.description
    await db.commit()
    await db.refresh(dept)
    return _department_response(dept)


@router.delete("/departments/{department_id}", status_code=204)
async def delete_department(
    department_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    result = await db.execute(select(Department).where(Department.id == uuid.UUID(department_id)))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    await _check_institution_access(dept.institution_id, user, db)
    await db.delete(dept)
    await db.commit()


# --- Services ---


@router.get("/institutions/{institution_id}/services", response_model=list[ServiceResponse])
async def list_services(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    inst_id = uuid.UUID(institution_id)
    await _check_institution_access(inst_id, user, db)
    result = await db.execute(
        select(Service)
        .join(Department, Service.department_id == Department.id)
        .where(Department.institution_id == inst_id)
    )
    return [_service_response(s) for s in result.scalars().all()]


@router.post("/services", response_model=ServiceResponse, status_code=201)
async def create_service(
    body: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    dept_result = await db.execute(
        select(Department).where(Department.id == uuid.UUID(body.department_id))
    )
    dept = dept_result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    await _check_institution_access(dept.institution_id, user, db)

    office_id = uuid.UUID(body.office_id) if body.office_id else None
    service = Service(
        department_id=dept.id,
        office_id=office_id,
        name=body.name,
        description=body.description,
        example_phrasings=body.example_phrasings,
        required_documents=body.required_documents,
        typical_duration=body.typical_duration,
        fees=body.fees,
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return _service_response(service)


@router.put("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    body: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    result = await db.execute(select(Service).where(Service.id == uuid.UUID(service_id)))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    dept_result = await db.execute(
        select(Department).where(Department.id == service.department_id)
    )
    dept = dept_result.scalar_one()
    await _check_institution_access(dept.institution_id, user, db)

    for field in ("name", "description", "example_phrasings", "required_documents", "typical_duration", "fees"):
        val = getattr(body, field)
        if val is not None:
            setattr(service, field, val)
    if body.office_id is not None:
        service.office_id = uuid.UUID(body.office_id)
    # Clear embedding so it gets regenerated
    service.embedding = None
    await db.commit()
    await db.refresh(service)
    return _service_response(service)


@router.delete("/services/{service_id}", status_code=204)
async def delete_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    result = await db.execute(select(Service).where(Service.id == uuid.UUID(service_id)))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    dept_result = await db.execute(
        select(Department).where(Department.id == service.department_id)
    )
    dept = dept_result.scalar_one()
    await _check_institution_access(dept.institution_id, user, db)
    await db.delete(service)
    await db.commit()


@router.post("/services/{service_id}/refresh-embedding", response_model=ServiceResponse)
async def refresh_service_embedding(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles("officer", "admin")),
):
    """Regenerate embedding for a single service after edits."""
    from app.agent.embeddings import get_embedding

    result = await db.execute(select(Service).where(Service.id == uuid.UUID(service_id)))
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    dept_result = await db.execute(
        select(Department).where(Department.id == service.department_id)
    )
    dept = dept_result.scalar_one()
    await _check_institution_access(dept.institution_id, user, db)

    text_parts = [f"Service: {service.name}", f"Description: {service.description}"]
    if service.example_phrasings:
        text_parts.append("Example requests: " + " | ".join(service.example_phrasings))
    service.embedding = await get_embedding("\n".join(text_parts))
    await db.commit()
    await db.refresh(service)
    return _service_response(service)
