import hashlib

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.database import get_connection


router = APIRouter()


class AuthPayload(BaseModel):
    username: str
    password: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def ensure_account_table(conn):
    sql = """
        CREATE TABLE IF NOT EXISTS Account (
            AccountID INT AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(50) NOT NULL UNIQUE,
            PasswordHash VARCHAR(64) NOT NULL,
            Role VARCHAR(20) NOT NULL DEFAULT 'admin',
            CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """
    with conn.cursor() as cursor:
        cursor.execute(sql)


@router.post("/register")
def register(payload: AuthPayload):
    username = payload.username.strip()
    password = payload.password.strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    conn = get_connection()
    try:
        ensure_account_table(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO Account (Username, PasswordHash, Role)
                    VALUES (%s, %s, 'admin')
                """,
                (username, hash_password(password)),
            )
            account_id = cursor.lastrowid
        conn.commit()
        return {
            "message": "注册成功",
            "account": {"AccountID": account_id, "Username": username, "Role": "admin"},
        }
    except Exception as exc:
        conn.rollback()
        message = str(exc)
        if "Duplicate" in message or "1062" in message:
            raise HTTPException(status_code=400, detail="用户名已存在")
        raise HTTPException(status_code=500, detail=message)
    finally:
        conn.close()


@router.post("/login")
def login(payload: AuthPayload):
    username = payload.username.strip()
    password = payload.password.strip()
    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    conn = get_connection()
    try:
        ensure_account_table(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    SELECT AccountID, Username, Role
                    FROM Account
                    WHERE Username = %s AND PasswordHash = %s
                """,
                (username, hash_password(password)),
            )
            account = cursor.fetchone()
        conn.commit()
        if account is None:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        return {"message": "登录成功", "account": account}
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        conn.close()
