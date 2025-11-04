import pymysql

# 所有一次性常量集中管理
MYSQL_CONFIG = dict(
    host="127.0.0.1", port=3306, user="fastapi",
    password="Fastapi@123", database="chat_db",
    charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor
)

EMBEDDING_MODEL = "/home/ldf/bigmodel/ChatGLM3/rag/paraphrase-multilingual-MiniLM-L12-v2"
OLLAMA_URL = "http://10.255.1.89:11434/api/generate"
DEFAULT_MILVUS_PATH = "/keeson/code/lwd/upload/medical_system/rag_api/A.db"
DEFAULT_COLLECTION = "medical_papers"
SIMILARITY_THRESHOLD = 2