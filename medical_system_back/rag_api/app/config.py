import pymysql

# 所有一次性常量集中管理
MYSQL_CONFIG = dict(
    host="127.0.0.1", port=3306, user="",
    password="", database="",
    charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor
)

EMBEDDING_MODEL = ""
OLLAMA_URL = "http://youip:11434/api/generate"
DEFAULT_MILVUS_PATH = "medical_system_back/rag_api/A.db"
DEFAULT_COLLECTION = "medical_papers"
SIMILARITY_THRESHOLD = 2
