import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="RESEARCH_CLERK", nullable=False)  # JUDGE, RESEARCH_CLERK, REGISTRAR, ADMIN
    court_division: Mapped[str] = mapped_column(String(255), default="Commercial Appellate Division, High Court")
    chambers_number: Mapped[str] = mapped_column(String(50), default="Chambers 402")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    dossiers = relationship("Dossier", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    saved_researches = relationship("SavedResearch", back_populates="user", cascade="all, delete-orphan")
