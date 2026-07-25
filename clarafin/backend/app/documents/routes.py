import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import clarafin.backend.app.db.session as session
from clarafin.backend.app.db.models import DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user_id: int = Depends(session.get_current_user_id)
):
    # Detect extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext == '.pdf':
        doc_type = 'PDF'
    elif ext == '.csv':
        doc_type = 'CSV'
    elif ext in ['.xlsx', '.xls']:
        doc_type = 'XLSX'
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF, CSV, or XLSX.")
        
    # Save file
    file_id = str(uuid.uuid4())
    saved_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    content = await file.read()
    file_size = len(content)
    with open(file_path, "wb") as f:
        f.write(content)
        
    # Save metadata to DB
    conn = session.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (user_id, filename, file_path, doc_type, file_size) VALUES (?, ?, ?, ?, ?)",
        (current_user_id, file.filename, file_path, doc_type, file_size)
    )
    conn.commit()
    doc_id = cursor.lastrowid
    
    cursor.execute("SELECT id, filename, doc_type, upload_date, file_size FROM documents WHERE id = ?", (doc_id,))
    doc_row = cursor.fetchone()
    conn.close()
    
    return dict(doc_row)

@router.get("", response_model=List[DocumentResponse])
def list_documents(current_user_id: int = Depends(session.get_current_user_id)):
    conn = session.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, filename, doc_type, upload_date, file_size FROM documents WHERE user_id = ? ORDER BY upload_date DESC",
        (current_user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
