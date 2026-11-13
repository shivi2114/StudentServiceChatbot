from fastapi import APIRouter
from backend.app.api.auth import router as auth_router
from backend.app.api.students import router as students_router
from backend.app.api.complaints import router as complaints_router
from backend.app.api.announcements import router as announcements_router
from backend.app.api.chat import router as chat_router
from backend.app.api.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(students_router)
api_router.include_router(complaints_router)
api_router.include_router(announcements_router)
api_router.include_router(chat_router)
api_router.include_router(admin_router)
