from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class AuditLogDTO(BaseModel):
    id: str
    timestamp: datetime
    chambers_user: str
    action: str
    target: str
    court_division: str
    endpoint: str
    ip_address: str
    metadata_payload: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class AuditLogCreateDTO(BaseModel):
    action: str
    target: str
    endpoint: Optional[str] = ""
    metadata_payload: Optional[Dict[str, Any]] = None
