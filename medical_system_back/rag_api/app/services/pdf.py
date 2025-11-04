import fitz, re, time, traceback
from io import BytesIO
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient, DataType
from ..db import get_db
from ..models import ProcessConfig

def process_pdfs_from_db(config: ProcessConfig):
    try:
        with get_db() as db:
            with db.cursor() as cur:
                cur.execute("SELECT id, filename, file_data FROM uploaded_files")
                rows = cur.fetchall()
            if not rows:
                return {"status": "empty", "message": "数据库中没有 PDF 文件"}

        model = SentenceTransformer(config.model_path)
        chunks, meta = [], []
        for r in rows:
            doc = fitz.open(stream=BytesIO(r["file_data"]), filetype="pdf")
            for p, page in enumerate(doc, 1):
                text = re.sub(r"\s+", "", page.get_text()).strip()
                if not text:
                    continue
                for i in range(0, len(text), 500):
                    chunk = text[i:i+500]
                    chunks.append(chunk)
                    meta.append({"page_num": p, "source": r["filename"]})

        embeddings = model.encode(chunks, normalize_embeddings=True)

        client = MilvusClient(config.db_path)
        coll = config.collection_name
        if client.has_collection(coll):
            client.drop_collection(coll)

        schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("vector", DataType.FLOAT_VECTOR, dim=embeddings.shape[1])
        schema.add_field("text", DataType.VARCHAR, max_length=65535)
        schema.add_field("page_num", DataType.INT64)
        schema.add_field("source", DataType.VARCHAR, max_length=255)

        idx = client.prepare_index_params()
        idx.add_index("vector", index_type="AUTOINDEX", metric_type="IP")
        client.create_collection(coll, schema=schema, index_params=idx)

        data = [{"id": i, "vector": v.tolist(), "text": t, "page_num": m["page_num"], "source": m["source"]}
                for i, (t, v, m) in enumerate(zip(chunks, embeddings, meta))]
        for i in range(0, len(data), 100):
            client.insert(coll, data[i:i+100])

        return {"status": "success", "message": f"{len(rows)} 个 PDF 已处理并写入 Milvus"}
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}