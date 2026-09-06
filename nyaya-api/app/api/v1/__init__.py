from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.statutes import router as statutes_router
from app.api.v1.cases import router as cases_router
from app.api.v1.dossiers import router as dossiers_router
from app.api.v1.research import router as research_router
from app.api.v1.audit import router as audit_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(statutes_router)
api_router.include_router(cases_router)
api_router.include_router(dossiers_router)
api_router.include_router(research_router)
api_router.include_router(audit_router)

__all__ = ["api_router"]

