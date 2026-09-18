from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import get_db


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get("/database")
def database_health(
    db: DatabaseSession,
):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "unavailable",
        }