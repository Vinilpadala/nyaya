from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.core.errors import UnauthorizedException
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserDTO, ChambersDemoUserDTO
from app.schemas.common import ResponseEnvelope
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Judicial Authentication & Chambers"])

DEMO_ACCOUNTS = [
    ChambersDemoUserDTO(
        email="justice.sharma@commercialcourt.gov.in",
        password="Chambers@2026",
        full_name="Hon'ble Justice A. K. Sharma — DEMO ACCOUNT",
        role="JUDGE",
        court_division="Commercial Appellate Division, High Court of Delhi",
        chambers_number="Courtroom 14 / Chambers 402",
        description="Presiding Commercial Division Judge with judicial memo & private deliberation privileges (SIH Demo Account)",
    ),
    ChambersDemoUserDTO(
        email="clerk.verma@commercialcourt.gov.in",
        password="Chambers@2026",
        full_name="R. K. Verma, Law Clerk (DEMO ACCOUNT)",
        role="RESEARCH_CLERK",
        court_division="Commercial Appellate Division, High Court of Delhi",
        chambers_number="Chambers 402 Library Desk",
        description="Judicial Research Assistant authorized to prepare case dossiers and legal ratios (SIH Demo Account)",
    ),
    ChambersDemoUserDTO(
        email="registrar.commercial@delhihighcourt.nic.in",
        password="Chambers@2026",
        full_name="P. N. Gupta, Registrar (DEMO ACCOUNT)",
        role="REGISTRAR",
        court_division="Commercial Registry & Case Management",
        chambers_number="Registry Wing Room 108",
        description="Court Registry Administrator supervising commercial dockets and cause lists (SIH Demo Account)",
    ),
]


@router.post("/login", response_model=ResponseEnvelope[TokenResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate chambers user and issue JWT access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise UnauthorizedException("Invalid chambers credentials or unregistered email")
    
    if not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedException("Invalid chambers credentials")
    
    if not user.is_active:
        raise UnauthorizedException("Chambers account has been deactivated")

    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "division": user.court_division,
    }
    token = create_access_token(data=token_data)

    return ResponseEnvelope(
        data=TokenResponse(
            access_token=token,
            token_type="Bearer",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            user=UserDTO.model_validate(user),
        )
    )


@router.get("/me", response_model=ResponseEnvelope[UserDTO])
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve the active judicial user's profile and credentials."""
    return ResponseEnvelope(data=UserDTO.model_validate(current_user))


@router.get("/demo-users", response_model=ResponseEnvelope[List[ChambersDemoUserDTO]])
def get_demo_users():
    """Retrieve pre-configured chambers accounts for development inspection and quick login."""
    return ResponseEnvelope(data=DEMO_ACCOUNTS)
