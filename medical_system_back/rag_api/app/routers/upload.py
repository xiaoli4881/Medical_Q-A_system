from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from .. db import get_db

router = APIRouter(prefix="/api", tags=["upload"])

@router.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "仅支持 PDF 文件")
    data = await file.read()
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute("INSERT INTO uploaded_files (filename,content_type,file_data) VALUES (%s,%s,%s)",
                        (file.filename, file.content_type, data))
    return {"success": True, "filename": file.filename}

@router.get("/list_pdfs")
def list_pdfs():
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute("SELECT id,filename FROM uploaded_files ORDER BY uploaded_at DESC")
            return cur.fetchall()

@router.get("/download_pdf/{file_id}")
def download_pdf(file_id: int):
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute("SELECT filename,content_type,file_data FROM uploaded_files WHERE id=%s", (file_id,))
            row = cur.fetchone()
    if not row:
        raise HTTPException(404, "文件不存在")
    return StreamingResponse(BytesIO(row["file_data"]),
                             media_type=row["content_type"],
                             headers={"Content-Disposition": f"attachment; filename={row['filename']}"})