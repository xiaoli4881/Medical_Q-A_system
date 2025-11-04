from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import upload, session, message
from .services.pdf import process_pdfs_from_db
from .models import ProcessConfig, ChatRequest
from .services.chat import rag_chat, call_llm, build_prompt_with_history

app = FastAPI(title="RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(upload)
app.include_router(session)
app.include_router(message)

# 独立业务接口
@app.post("/api/process_pdfs")
def api_process_pdfs(cfg: ProcessConfig):
    return process_pdfs_from_db(cfg)

@app.post("/api/rag_chat")
def api_rag_chat(req: ChatRequest):
    return rag_chat(req)

@app.post("/api/chat")
def api_chat(req: ChatRequest):
    prompt = build_prompt_with_history(req.session_id, req.prompt) if req.session_id else req.prompt
    return {"text": call_llm(req.model, prompt)}