from typing import Optional, List
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.core.errors import UnauthorizedException, ForbiddenException
from app.db.session import get_db
from app.models.user import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate JWT token from Authorization header and return User."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Authorization header missing or invalid format (Bearer token required)")
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired session token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token payload malformed")
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        user_email = payload.get("email")
        if user_email:
            user = db.query(User).filter(User.email == user_email, User.is_active == True).first()

    if not user:
        raise UnauthorizedException("User account not found or deactivated")

    
    return user


def require_role(roles: List[str]):
    """Role-based authorization dependency factory."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(f"Role '{current_user.role}' not permitted. Requires one of: {', '.join(roles)}")
        return current_user
    return role_checker
