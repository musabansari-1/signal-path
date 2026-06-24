from fastapi import APIRouter

from app.api.routes.applications import router as applications_router
from app.api.routes.artifacts import router as artifacts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.career_profile import router as career_profile_router
from app.api.routes.health import router as health_router
from app.api.routes.interview_prep import router as interview_prep_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.portfolio import router as portfolio_router
from app.api.routes.projects import router as projects_router
from app.api.routes.role_criteria import router as role_criteria_router
from app.api.routes.weekly_plan import router as weekly_plan_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(career_profile_router)
api_router.include_router(role_criteria_router)
api_router.include_router(jobs_router)
api_router.include_router(artifacts_router)
api_router.include_router(applications_router)
api_router.include_router(interview_prep_router)
api_router.include_router(portfolio_router)
api_router.include_router(weekly_plan_router)
