from typing import Generic, TypeVar, Optional, Any, Dict
from datetime import datetime, timezone
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    pages: int


class ResponseEnvelope(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: Dict[str, Any] = Field(
        default_factory=lambda: {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chambers_system": "Nyaya AI v0.1.0",
        }
    )


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorDetail
