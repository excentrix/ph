from fastapi import APIRouter
from services.api.routes.chat import router as chat_router

# Create main router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

__all__ = ["api_router"]
