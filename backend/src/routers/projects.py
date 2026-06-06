from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.database import get_connection


router = APIRouter()


class StatusUpdate(BaseModel):
    status: str


class CompetitionProjectCreate(BaseModel):
    project_name: str
    team_id: int
    teacher_id: int
    competition_id: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    registration_status: str = "已报名"


class ResearchProjectCreate(BaseModel):
    project_name: str
    team_id: int
    teacher_id: int
    source: Optional[str] = None
    research_level: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


@router.get("")
def list_projects():
    sql = """
        SELECT
            p.ProjectID,
            p.ProjectName,
            p.ProjectType,
            p.ProjectStatus,
            t.TeamName,
            u.UserName AS TeacherName
        FROM Project p
        LEFT JOIN Team t ON p.TeamID = t.TeamID
        LEFT JOIN Teacher te ON p.TeacherID = te.UserID
        LEFT JOIN Users u ON te.UserID = u.UserID
        ORDER BY p.ProjectID
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


@router.post("/competition")
def create_competition_project(payload: CompetitionProjectCreate):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO Registration (TeamID, CompetitionID, RegisterTime, Status)
                    VALUES (%s, %s, CURDATE(), %s)
                """,
                (payload.team_id, payload.competition_id, payload.registration_status),
            )
            cursor.execute(
                """
                    INSERT INTO Project
                        (ProjectName, ProjectType, StartDate, EndDate, ProjectStatus, TeamID, TeacherID)
                    VALUES
                        (%s, '竞赛项目', COALESCE(%s, CURDATE()), %s, '进行中', %s, %s)
                """,
                (
                    payload.project_name,
                    payload.start_date,
                    payload.end_date,
                    payload.team_id,
                    payload.teacher_id,
                ),
            )
            project_id = cursor.lastrowid
            cursor.execute(
                """
                    INSERT INTO Competition_Project (ProjectID, CompetitionID)
                    VALUES (%s, %s)
                """,
                (project_id, payload.competition_id),
            )
        conn.commit()
        return {"message": "竞赛报名及项目创建成功", "project_id": project_id}
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.post("/research")
def create_research_project(payload: ResearchProjectCreate):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO Project
                        (ProjectName, ProjectType, StartDate, EndDate, ProjectStatus, TeamID, TeacherID)
                    VALUES
                        (%s, '科研项目', COALESCE(%s, CURDATE()), %s, '进行中', %s, %s)
                """,
                (
                    payload.project_name,
                    payload.start_date,
                    payload.end_date,
                    payload.team_id,
                    payload.teacher_id,
                ),
            )
            project_id = cursor.lastrowid
            cursor.execute(
                """
                    INSERT INTO Research_Project (ProjectID, Source, ResearchLevel)
                    VALUES (%s, %s, %s)
                """,
                (project_id, payload.source, payload.research_level),
            )
        conn.commit()
        return {"message": "科研项目创建成功", "project_id": project_id}
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.delete("/{project_id}")
def delete_project(project_id: int):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Achievement WHERE ProjectID = %s", (project_id,))
            cursor.execute("DELETE FROM Funding WHERE ProjectID = %s", (project_id,))
            cursor.execute("DELETE FROM Competition_Project WHERE ProjectID = %s", (project_id,))
            cursor.execute("DELETE FROM Research_Project WHERE ProjectID = %s", (project_id,))
            cursor.execute("DELETE FROM Project WHERE ProjectID = %s", (project_id,))
            if cursor.rowcount == 0:
                conn.rollback()
                raise HTTPException(status_code=404, detail="项目不存在")
        conn.commit()
        return {"message": "项目及其关联记录已通过事务删除", "project_id": project_id}
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()


@router.put("/{project_id}/status")
def update_project_status(project_id: int, payload: StatusUpdate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("sp_UpdateProjectStatus", (project_id, payload.status))
            cursor.execute(
                "SELECT ProjectID, ProjectName, ProjectStatus FROM Project WHERE ProjectID = %s",
                (project_id,),
            )
            row = cursor.fetchone()
        conn.commit()
        if row is None:
            raise HTTPException(status_code=404, detail="项目不存在")
        return row
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()
