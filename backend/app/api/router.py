from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.career_profile import router as career_profile_router
from app.api.routes.health import router as health_router
from app.api.routes.projects import router as projects_router
from app.api.routes.role_criteria import router as role_criteria_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(career_profile_router)
api_router.include_router(role_criteria_router)
