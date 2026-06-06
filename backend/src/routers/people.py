from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.database import get_connection


router = APIRouter()


class StudentCreate(BaseModel):
    user_name: str
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    stu_no: str
    college: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None


class TeacherCreate(BaseModel):
    user_name: str
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    teacher_no: str
    college: Optional[str] = None
    title: Optional[str] = None


@router.get("/students")
def list_students():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT u.UserID, u.UserName, u.Gender, u.Phone, u.Email,
                           s.StuNo, s.College, s.Major, s.Grade
                    FROM Student s
                    JOIN Users u ON s.UserID = u.UserID
                    ORDER BY u.UserID
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()


@router.post("/students")
def create_student(payload: StudentCreate):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO Users (UserName, Gender, Phone, Email)
                    VALUES (%s, %s, %s, %s)
                """,
                (payload.user_name, payload.gender, payload.phone, payload.email),
            )
            user_id = cursor.lastrowid
            cursor.execute(
                """
                    INSERT INTO Student (UserID, StuNo, College, Major, Grade)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, payload.stu_no, payload.college, payload.major, payload.grade),
            )
        conn.commit()
        return {"message": "学生创建成功", "user_id": user_id}
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.get("/teachers")
def list_teachers():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT u.UserID, u.UserName, u.Gender, u.Phone, u.Email,
                           t.TeacherNo, t.College, t.Title
                    FROM Teacher t
                    JOIN Users u ON t.UserID = u.UserID
                    ORDER BY u.UserID
                """
            )
            return cursor.fetchall()
    finally:
        conn.close()


@router.post("/teachers")
def create_teacher(payload: TeacherCreate):
    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO Users (UserName, Gender, Phone, Email)
                    VALUES (%s, %s, %s, %s)
                """,
                (payload.user_name, payload.gender, payload.phone, payload.email),
            )
            user_id = cursor.lastrowid
            cursor.execute(
                """
                    INSERT INTO Teacher (UserID, TeacherNo, College, Title)
                    VALUES (%s, %s, %s, %s)
                """,
                (user_id, payload.teacher_no, payload.college, payload.title),
            )
        conn.commit()
        return {"message": "教师创建成功", "user_id": user_id}
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()

