import uuid
from typing import List
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Statute(Base):
    __tablename__ = "statutes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    short_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    act_number: Mapped[str] = mapped_column(String(100), nullable=False)
    enactment_year: Mapped[int] = mapped_column(Integer, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(100), default="India (Central)")
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=True)

    sections: Mapped[List["StatuteSection"]] = relationship(
        "StatuteSection", back_populates="statute", cascade="all, delete-orphan"
    )


class StatuteSection(Base):
    __tablename__ = "statute_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    statute_id: Mapped[str] = mapped_column(String(36), ForeignKey("statutes.id", ondelete="CASCADE"), nullable=False)
    section_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    heading: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_amended: Mapped[bool] = mapped_column(Boolean, default=False)
    amendment_notes: Mapped[str] = mapped_column(String(500), default="")
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=True)

    statute: Mapped["Statute"] = relationship("Statute", back_populates="sections")
