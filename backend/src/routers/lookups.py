from fastapi import APIRouter

from src.database import get_connection


router = APIRouter()


@router.get("/teams")
def list_teams():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT TeamID, TeamName
                    FROM Team
                    ORDER BY TeamID
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()


@router.get("/competitions")
def list_competitions():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT
                        CompetitionID,
                        CompetitionName,
                        CompetitionLevel,
                        StartDate,
                        EndDate
                    FROM Competition
                    ORDER BY CompetitionID
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()

