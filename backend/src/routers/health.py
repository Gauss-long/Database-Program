from fastapi import APIRouter

from src.config.settings import settings


router = APIRouter(tags=["health"])


@router.get("/")
def index():
    return {"message": "高校竞赛项目管理系统后端已启动"}


@router.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "database": settings.db_name,
        "connection": settings.connection_string,
    }

