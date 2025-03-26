# Import all API routers
from fastapi import APIRouter
from app.api.endpoints.email_processor import router as email_router

api_router = APIRouter()
api_router.include_router(email_router)
