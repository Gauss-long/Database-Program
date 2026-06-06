from fastapi import APIRouter

from src.database import get_connection


router = APIRouter()


@router.get("/project-summary")
def project_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM v_ProjectSummary ORDER BY ProjectID")
            return cursor.fetchall()
    finally:
        conn.close()


@router.get("/dashboard")
def dashboard():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM Project")
            project_total = cursor.fetchone()["total"]
            cursor.execute("SELECT COUNT(*) AS total FROM Competition")
            competition_total = cursor.fetchone()["total"]
            cursor.execute("SELECT COUNT(*) AS total FROM Team")
            team_total = cursor.fetchone()["total"]
            cursor.execute("SELECT COUNT(*) AS total FROM Achievement")
            achievement_total = cursor.fetchone()["total"]
            cursor.execute(
                "SELECT ProjectStatus AS name, COUNT(*) AS value FROM Project GROUP BY ProjectStatus"
            )
            status_distribution = cursor.fetchall()
        return {
            "project_total": project_total,
            "competition_total": competition_total,
            "team_total": team_total,
            "achievement_total": achievement_total,
            "status_distribution": status_distribution,
        }
    finally:
        conn.close()

