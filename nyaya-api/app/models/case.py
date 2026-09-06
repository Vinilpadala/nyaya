import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import String, Boolean, Text, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    neutral_citation: Mapped[str] = mapped_column(String(100), index=True, default="")
    standard_citation: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    court: Mapped[str] = mapped_column(String(255), nullable=False)
    judgment_date: Mapped[date] = mapped_column(Date, nullable=False)
    bench_quorum: Mapped[str] = mapped_column(String(500), nullable=False)
    bench_strength: Mapped[int] = mapped_column(Integer, default=2)
    commercial_category: Mapped[str] = mapped_column(String(255), default="Commercial Dispute")
    jurisdiction: Mapped[str] = mapped_column(String(100), default="ALL", index=True)
    source_provenance: Mapped[str] = mapped_column(String(255), default="Supreme Court Cases (SCC) / Official Law Reports")
    ratio_decidendi: Mapped[str] = mapped_column(Text, nullable=False)
    full_text_snippet: Mapped[str] = mapped_column(Text, default="")
    is_good_law: Mapped[bool] = mapped_column(Boolean, default=True)
    status_summary: Mapped[str] = mapped_column(String(255), default="Settled Law")
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=True)

    citations_made: Mapped[List["Citation"]] = relationship(
        "Citation",
        foreign_keys="[Citation.source_case_id]",
        back_populates="source_case",
        cascade="all, delete-orphan",
    )
    passages: Mapped[List["CasePassage"]] = relationship(
        "CasePassage",
        back_populates="case",
        cascade="all, delete-orphan",
    )


class CasePassage(Base):
    __tablename__ = "case_passages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    passage_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    paragraph_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passage_text: Mapped[str] = mapped_column(Text, nullable=False)
    significance: Mapped[str] = mapped_column(String(500), default="")
    is_ratio: Mapped[bool] = mapped_column(Boolean, default=False)
    source_provenance: Mapped[str] = mapped_column(String(255), default="Supreme Court Reports (SCR) / Official Record")

    case: Mapped["Case"] = relationship("Case", back_populates="passages")


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    cited_case_name: Mapped[str] = mapped_column(String(500), nullable=False)
    cited_case_citation: Mapped[str] = mapped_column(String(255), default="")
    treatment: Mapped[str] = mapped_column(String(50), default="AFFIRMED")  # AFFIRMED, OVERRULED, DISTINGUISHED, CONSIDERED
    pinpoint_paragraph: Mapped[str] = mapped_column(String(100), default="para 1")

    source_case: Mapped["Case"] = relationship("Case", foreign_keys=[source_case_id], back_populates="citations_made")

