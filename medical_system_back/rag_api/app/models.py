from pydantic import BaseModel
from typing import List, Optional

class ProcessConfig(BaseModel):
    db_path: str = "/keeson/code/lwd/upload/medical_system/rag_api/A.db"
    collection_name: str = "medical_papers"
    model_path: str = "/home/ldf/bigmodel/ChatGLM3/rag/paraphrase-multilingual-MiniLM-L12-v2"

class ChatRequest(BaseModel):
    prompt: str
    model: str = "qwen2.5:7b"
    session_id: Optional[int] = None
    milvus_db_path: Optional[str] = None
    collection_name: Optional[str] = None
    top_k: Optional[int] = 10
    rerank_top: Optional[int] = 1

class SessionCreate(BaseModel):
    title: str

class MessageCreate(BaseModel):
    session_id: int
    role: str
    content: str

class Document(BaseModel):
    text: str
    page_num: int
    source: str
    similarity_score: float
    rerank_score: Optional[float] = None

class RAGResponse(BaseModel):
    question: str
    retrieved_documents: List[Document]
    reranked_documents: List[Document]
    top_documents: List[Document]