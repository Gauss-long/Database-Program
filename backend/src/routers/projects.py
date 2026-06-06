from fastapi import APIRouter, HTTPException

from src.database import get_connection


router = APIRouter()


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
def update_project_status(project_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.callproc("sp_UpdateProjectStatus", (project_id,))
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

