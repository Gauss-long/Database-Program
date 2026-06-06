from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.database import get_connection


router = APIRouter()


class TeamCreate(BaseModel):
    team_name: str
    leader_id: int
    create_date: Optional[date] = None


class MemberCreate(BaseModel):
    student_id: int


@router.get("")
def list_teams():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT t.TeamID, t.TeamName, t.CreateDate, t.LeaderID,
                           u.UserName AS LeaderName,
                           COUNT(p.StudentID) AS MemberCount
                    FROM Team t
                    LEFT JOIN Student s ON t.LeaderID = s.UserID
                    LEFT JOIN Users u ON s.UserID = u.UserID
                    LEFT JOIN Participate p ON t.TeamID = p.TeamID
                    GROUP BY t.TeamID, t.TeamName, t.CreateDate, t.LeaderID, u.UserName
                    ORDER BY t.TeamID
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()


@router.post("")
def create_team(payload: TeamCreate):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO Team (TeamName, CreateDate, LeaderID)
                    VALUES (%s, COALESCE(%s, CURDATE()), %s)
                """,
                (payload.team_name, payload.create_date, payload.leader_id),
            )
            team_id = cursor.lastrowid
            cursor.execute(
                """
                    INSERT IGNORE INTO Participate (StudentID, TeamID)
                    VALUES (%s, %s)
                """,
                (payload.leader_id, team_id),
            )
        conn.commit()
        return {"message": "团队创建成功", "team_id": team_id}
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.get("/{team_id}/members")
def list_members(team_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT u.UserID, u.UserName, s.StuNo, s.College, s.Major, s.Grade
                    FROM Participate p
                    JOIN Student s ON p.StudentID = s.UserID
                    JOIN Users u ON s.UserID = u.UserID
                    WHERE p.TeamID = %s
                    ORDER BY u.UserID
                """,
                (team_id,),
            )
            return cursor.fetchall()
    finally:
        conn.close()


@router.post("/{team_id}/members")
def add_member(team_id: int, payload: MemberCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO Participate (StudentID, TeamID)
                    VALUES (%s, %s)
                """,
                (payload.student_id, team_id),
            )
        conn.commit()
        return {"message": "团队成员添加成功"}
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()

