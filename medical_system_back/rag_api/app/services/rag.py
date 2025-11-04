from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
from ..config import EMBEDDING_MODEL

class RAGSystem:
    def __init__(self, milvus_db_path: str, collection_name: str):
        self.client = MilvusClient(milvus_db_path)
        self.collection = collection_name
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def retrieve(self, question: str, top_k: int = 10):
        vec = self.model.encode([question], normalize_embeddings=True)[0].tolist()
        res = self.client.search(
            collection_name=self.collection,
            data=[vec],
            limit=top_k,
            output_fields=["text", "page_num", "source"]
        )[0]
        docs = []
        for hit in res:
            docs.append({
                "text": hit.entity["text"],
                "page_num": hit.entity["page_num"],
                "source": hit.entity["source"],
                "similarity_score": 1 - hit.distance   # cosine
            })
        return docs