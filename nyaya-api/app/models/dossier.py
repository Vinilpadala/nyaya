import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Dossier(Base):
    __tablename__ = "dossiers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    matter_title: Mapped[str] = mapped_column(String(500), nullable=False)
    suit_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    judicial_notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="dossiers")
    items: Mapped[List["DossierItem"]] = relationship("DossierItem", back_populates="dossier", cascade="all, delete-orphan")


class DossierItem(Base):
    __tablename__ = "dossier_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dossier_id: Mapped[str] = mapped_column(String(36), ForeignKey("dossiers.id", ondelete="CASCADE"), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), default="CASE")  # CASE, SECTION, NOTE
    reference_id: Mapped[str] = mapped_column(String(255), default="")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, default="")
    pinpoint: Mapped[str] = mapped_column(String(100), default="")

    dossier: Mapped["Dossier"] = relationship("Dossier", back_populates="items")
