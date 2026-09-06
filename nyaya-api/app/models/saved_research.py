import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SavedResearch(Base):
    __tablename__ = "saved_research"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    matter_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    case_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    jurisdiction: Mapped[str] = mapped_column(String(100), default="ALL")
    lead_citation: Mapped[str] = mapped_column(String(255), default="")
    lead_title: Mapped[str] = mapped_column(String(500), default="")
    summary_extract: Mapped[str] = mapped_column(Text, default="")
    confidence_score: Mapped[float] = mapped_column(Float, default=0.9)
    uncertainty_level: Mapped[str] = mapped_column(String(50), default="LOW")  # LOW, MEDIUM, HIGH
    notes: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(String(255), default="")
    full_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="saved_researches")
