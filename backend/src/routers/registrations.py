from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.database import get_connection


router = APIRouter()


class RegistrationCreate(BaseModel):
    team_id: int
    competition_id: int
    register_time: Optional[date] = None
    status: str = "已报名"


@router.post("")
def create_registration(payload: RegistrationCreate):
    sql = """
        INSERT INTO Registration (TeamID, CompetitionID, RegisterTime, Status)
        VALUES (%s, %s, COALESCE(%s, CURDATE()), %s)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (
                    payload.team_id,
                    payload.competition_id,
                    payload.register_time,
                    payload.status,
                ),
            )
            registration_id = cursor.lastrowid
        conn.commit()
        return {"message": "报名成功", "registration_id": registration_id}
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()

