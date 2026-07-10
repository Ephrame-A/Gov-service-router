"""SQLAlchemy 2.0 models for the Government Service Router database."""

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Double,
    ForeignKey,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)  # federal | regional | municipal
    description: Mapped[str | None] = mapped_column(Text)
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    departments: Mapped[list["Department"]] = relationship(back_populates="institution", cascade="all, delete-orphan")
    offices: Mapped[list["Office"]] = relationship(back_populates="institution", cascade="all, delete-orphan")
    users: Mapped[list["User"]] = relationship(back_populates="institution")


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    institution: Mapped["Institution"] = relationship(back_populates="departments")
    services: Mapped[list["Service"]] = relationship(back_populates="department", cascade="all, delete-orphan")


class Office(Base):
    __tablename__ = "offices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False
    )
    address: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float | None] = mapped_column(Double)
    lng: Mapped[float | None] = mapped_column(Double)
    working_hours: Mapped[str | None] = mapped_column(Text)
    contact_phone: Mapped[str | None] = mapped_column(Text)
    contact_email: Mapped[str | None] = mapped_column(Text)

    institution: Mapped["Institution"] = relationship(back_populates="offices")
    services: Mapped[list["Service"]] = relationship(back_populates="office")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False
    )
    office_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("offices.id", ondelete="SET NULL")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    example_phrasings: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'")
    )
    required_documents: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, server_default=text("'{}'")
    )
    typical_duration: Mapped[str | None] = mapped_column(Text)
    fees: Mapped[str | None] = mapped_column(Text)
    embedding = mapped_column(Vector(settings.EMBEDDING_DIM))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    department: Mapped["Department"] = relationship(back_populates="services")
    office: Mapped["Office | None"] = relationship(back_populates="services")


class CitizenQuery(Base):
    __tablename__ = "citizen_queries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_intent = mapped_column(JSONB)
    matched_service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("services.id")
    )
    confidence_score: Mapped[float | None] = mapped_column(Double)
    clarification_asked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    feedback: Mapped[str | None] = mapped_column(Text)  # 'correct' | 'incorrect' | NULL
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)  # citizen | officer | admin
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    institution: Mapped["Institution | None"] = relationship(back_populates="users")
