import requests, time
from ..db import get_db
from ..config import OLLAMA_URL, SIMILARITY_THRESHOLD
from .rag import RAGSystem

def build_prompt_with_history(session_id: int, prompt: str) -> str:
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute("""
                SELECT role,content FROM chat_messages
                WHERE session_id=%s ORDER BY created_at DESC LIMIT 10
            """, (session_id,))
            hist = cur.fetchall()
    if not hist:
        return prompt
    hist.reverse()
    ctx = "对话历史：\n" + "\n".join(
        f"{'用户' if h['role']=='user' else '助手'}: {h['content']}" for h in hist
    )
    return f"{ctx}\n当前问题：{prompt}"

def call_llm(model: str, prompt: str) -> str:
    resp = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=120)
    resp.raise_for_status()
    return resp.json().get("response", "（无响应）")

def rag_chat(req):
    prompt = build_prompt_with_history(req.session_id, req.prompt) if req.session_id else req.prompt
    docs = RAGSystem(req.milvus_db_path or DEFAULT_MILVUS_PATH,
                     req.collection_name or DEFAULT_COLLECTION).retrieve(req.prompt, req.top_k)
    filtered = [d for d in docs if d["similarity_score"] <= SIMILARITY_THRESHOLD][:2]
    if filtered:
        prompt += "\n\n相关文档内容如下：\n"
        for d in filtered:
            prompt += f"📄 来源: {d['source']} (页 {d['page_num']}) 相似度: {d['similarity_score']:.4f}\n内容: {d['text']}\n\n"
    reply = call_llm(req.model, prompt)

    # 持久化
    if req.session_id:
        with get_db() as db:
            with db.cursor() as cur:
                cur.execute("INSERT INTO chat_messages (session_id,role,content) VALUES (%s,%s,%s)",
                            (req.session_id, "user", req.prompt))
                cur.execute("INSERT INTO chat_messages (session_id,role,content) VALUES (%s,%s,%s)",
                            (req.session_id, "assistant", reply))
                for d in filtered:
                    cur.execute("""INSERT INTO chat_documents
                        (session_id,source,page_num,similarity_score,text)
                        VALUES (%s,%s,%s,%s,%s)""",
                        (req.session_id, d["source"], d["page_num"], d["similarity_score"], d["text"]))
    return {"text": reply, "top_documents": filtered}