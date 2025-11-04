from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from ..db import get_db

router = APIRouter(prefix="/api", tags=["message"])

class MessageCreate(BaseModel):
    session_id: int
    role: str
    content: str

# 发送一条消息（仅保存）
@router.post("/messages")
def add_message(msg: MessageCreate):
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (%s,%s,%s)",
                (msg.session_id, msg.role, msg.content)
            )
    return {"success": True}

# 获取指定会话的完整历史（含 RAG 文档）
@router.get("/get_chat_history")
def get_chat_history(session_id: int = Query(...)):
    with get_db() as db:
        with db.cursor() as cur:
            # 消息
            cur.execute(
                """SELECT role, content, created_at
                   FROM chat_messages
                   WHERE session_id=%s
                   ORDER BY created_at ASC""",
                (session_id,)
            )
            msgs = cur.fetchall()
            # RAG 文档
            cur.execute(
                """SELECT source, page_num, similarity_score, text
                   FROM chat_documents
                   WHERE session_id=%s
                   ORDER BY created_at ASC""",
                (session_id,)
            )
            docs = cur.fetchall()

    # 把文档挂到最后一条 assistant 消息
    if docs:
        for m in reversed(msgs):
            if m["role"] == "assistant":
                m["source_docs"] = [
                    {
                        "source": d["source"],
                        "page_num": d["page_num"],
                        "similarity_score": d["similarity_score"],
                        "text": d["text"],
                    }
                    for d in docs
                ]
                break

    return {"messages": msgs}