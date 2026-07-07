from fastapi import APIRouter

from database.health import check_database

router = APIRouter(
    prefix="/api/v1",
    tags=["Health"]
)


@router.get("/health")
def health():

    db_status = check_database()

    return {

        "backend": "running",

        "database": "connected" if db_status else "disconnected",

        "status": "healthy" if db_status else "unhealthy"
    }