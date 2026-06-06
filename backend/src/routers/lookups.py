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


@router.get("/teachers")
def list_teachers():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT t.UserID, u.UserName, t.TeacherNo, t.Title
                    FROM Teacher t
                    JOIN Users u ON t.UserID = u.UserID
                    ORDER BY t.UserID
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()


@router.get("/students")
def list_students():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT s.UserID, u.UserName, s.StuNo, s.Major
                    FROM Student s
                    JOIN Users u ON s.UserID = u.UserID
                    ORDER BY s.UserID
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()
