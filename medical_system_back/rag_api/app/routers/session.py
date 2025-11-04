from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
from ..db import get_db
from typing import List

router = APIRouter(prefix="/api", tags=["session"])

class SessionCreate(BaseModel):
    title: str

# 获取所有会话（含消息）
@router.get("/sessions")
def get_sessions():
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM chat_sessions WHERE is_deleted=0 ORDER BY created_at ASC")
            sessions = cur.fetchall()
            for s in sessions:
                cur.execute(
                    "SELECT * FROM chat_messages WHERE session_id=%s ORDER BY created_at ASC",
                    (s["id"],)
                )
                s["messages"] = cur.fetchall()
                s["session_number"] = sessions.index(s) + 1
    return sessions

# 创建会话
@router.post("/sessions")
def create_session(req: SessionCreate):
    new_id = int(time.time() * 1000)
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute("INSERT INTO chat_sessions (id, title) VALUES (%s, %s)", (new_id, req.title))
    return {"id": new_id, "title": req.title}

# 逻辑删除会话
@router.delete("/sessions/{session_id}")
def delete_session(session_id: int):
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute("UPDATE chat_sessions SET is_deleted=1 WHERE id=%s", (session_id,))
    return {"success": True}

# 获取最近一条会话 ID（供前端快速跳转）
@router.get("/get_last_session")
def get_last_session():
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT session_id FROM chat_messages ORDER BY created_at DESC LIMIT 1"
            )
            row = cur.fetchone()
    return {"session_id": row["session_id"] if row else None}