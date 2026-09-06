from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class UserDTO(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    court_division: str
    chambers_number: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in_minutes: int
    user: UserDTO


class ChambersDemoUserDTO(BaseModel):
    email: str
    password: str
    full_name: str
    role: str
    court_division: str
    chambers_number: str
    description: str
