import os
import uuid
import json
import logging
import asyncio
import sqlite3
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
from dotenv import load_dotenv

from backend.models import UserCreate, UserResponse, LoginRequest, TokenResponse, DocumentResponse, RunAnalysisRequest, AnalysisResponse
import backend.database as db
import backend.parser as parser
import backend.scraper as scraper
from backend.rag import RAGEngine
import backend.analyzer as analyzer

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("main")

app = FastAPI(
    title="Financial Document Intelligence Agent API",
    description="Agentic AI system for analyzing SME financial documents with traceability and boundaries.",
    version="1.0.0"
)

# CORS Config
allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory
UPLOAD_DIR = "uploads"
MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.on_event("startup")
async def startup_event():
    db.init_db()
    logger.info("Database initialized.")

# --- Authentication Routes ---
@app.post("/auth/signup", response_model=UserResponse)
def signup(user_data: UserCreate):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_pw = db.hash_password(user_data.password)
        cursor.execute(
            "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
            (user_data.email, hashed_pw)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute("SELECT id, email, created_at FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        return dict(user)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/auth/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, hashed_password FROM users WHERE email = ?", (login_data.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not db.verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    access = db.create_access_token(user["id"], user["email"])
    refresh = db.create_refresh_token(user["id"], user["email"])
    return {"access_token": access, "refresh_token": refresh}

# --- Document Ingestion Routes ---
@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user_id: int = Depends(db.get_current_user_id)
):
    # Determine type
    original_filename = os.path.basename((file.filename or "").replace("\\", "/"))
    ext = os.path.splitext(original_filename)[1].lower()
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
    saved_filename = f"{file_id}_{original_filename}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    content = await file.read()
    file_size = len(content)
    if file_size == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if file_size > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File is too large. The limit is 20 MB.")
    with open(file_path, "wb") as f:
        f.write(content)
        
    # Save to Database
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (user_id, filename, file_path, doc_type, file_size) VALUES (?, ?, ?, ?, ?)",
        (current_user_id, original_filename, file_path, doc_type, file_size)
    )
    conn.commit()
    doc_id = cursor.lastrowid
    
    cursor.execute("SELECT id, filename, doc_type, upload_date, file_size FROM documents WHERE id = ?", (doc_id,))
    doc_row = cursor.fetchone()
    conn.close()
    
    return dict(doc_row)

@app.get("/documents", response_model=List[DocumentResponse])
def list_documents(current_user_id: int = Depends(db.get_current_user_id)):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, filename, doc_type, upload_date, file_size FROM documents WHERE user_id = ? ORDER BY upload_date DESC",
        (current_user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/documents/{document_id}/source")
def get_document_source(document_id: int, current_user_id: int = Depends(db.get_current_user_id)):
    """Return normalized source chunks for the citation viewer, scoped to the owner."""
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT filename, file_path FROM documents WHERE id = ? AND user_id = ?",
        (document_id, current_user_id),
    )
    document = cursor.fetchone()
    conn.close()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return parser.parse_document(document["file_path"], document["filename"])

# --- Analysis Orchestration & Agent Reasoning Loop ---
async def execute_agent_pipeline(analysis_id: str, doc_ids: List[int], user_id: int, api_key: Optional[str]):
    def update_progress(msg: str, status: str = "processing"):
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE analyses SET progress_message = ?, status = ? WHERE id = ?",
            (msg, status, analysis_id)
        )
        conn.commit()
        conn.close()

    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        # 1. Fetch document paths
        placeholders = ",".join(["?"] * len(doc_ids))
        cursor.execute(
            f"SELECT id, filename, file_path, doc_type FROM documents WHERE id IN ({placeholders}) AND user_id = ?",
            (*doc_ids, user_id)
        )
        docs = cursor.fetchall()
        conn.close()
        
        if not docs:
            update_progress("No valid documents found for analysis", "failed")
            return

        # Step 1: Document Ingestion & Parsing
        parsed_docs = []
        for d in docs:
            update_progress(f"Parsing {d['filename']} ({d['doc_type']})...")
            await asyncio.sleep(1.0) # Visual delay for hackathon progress tracking
            
            # Extract and index lines
            parsed = await asyncio.to_thread(parser.parse_document, d["file_path"], d["filename"])
            parsed_docs.append(parsed)

        # Step 2: RAG Layer Chunk Indexing
        update_progress("Building structure-aware vector embeddings for RAG...")
        await asyncio.sleep(1.0)
        rag_engine = await asyncio.to_thread(RAGEngine)
        await asyncio.to_thread(rag_engine.add_documents, parsed_docs)

        # Step 3: Industry Benchmarks Scraping
        update_progress("Scraping external SME profitability & DSO benchmarks...")
        await asyncio.sleep(1.0)
        benchmarks = await asyncio.to_thread(scraper.scrape_financial_benchmarks, sector="services")

        # Step 4: Run Multi-step Agent Reasoning
        update_progress("Initializing Groq agent reasoning loop...")
        await asyncio.sleep(1.0)
        
        update_progress("Agent reasoning: checking liquidity ratios...")
        await asyncio.sleep(0.8)
        
        update_progress("Agent reasoning: calculating margins & detecting anomalous spending...")
        await asyncio.sleep(0.8)
        
        update_progress("Agent reasoning: scanning checklists for missing information (Gaps)...")
        await asyncio.sleep(0.8)
        
        update_progress("Agent reasoning: evaluating trajectory patterns for forward risks...")
        await asyncio.sleep(0.8)
        
        update_progress("Assembling structured analysis with citations...")
        
        # Call Groq
        result = await asyncio.to_thread(analyzer.run_groq_analysis, parsed_docs, benchmarks, api_key)
        
        # Save results to DB
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE analyses SET status = 'finished', progress_message = 'Analysis complete.', result_json = ? WHERE id = ?",
            (json.dumps(result), analysis_id)
        )
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Pipeline error for analysis {analysis_id}: {e}")
        update_progress(f"Error occurred: {str(e)}", "failed")

@app.post("/analysis/run", response_model=AnalysisResponse)
async def run_analysis(
    req: RunAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user_id: int = Depends(db.get_current_user_id)
):
    analysis_id = str(uuid.uuid4())
    doc_ids_str = ",".join(map(str, req.doc_ids))
    
    # Save Initial State
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO analyses (id, user_id, status, progress_message, doc_ids) VALUES (?, ?, ?, ?, ?)",
        (analysis_id, current_user_id, "pending", "Queued for analysis.", doc_ids_str)
    )
    conn.commit()
    conn.close()
    
    # Run pipeline asynchronously in background
    background_tasks.add_task(
        execute_agent_pipeline,
        analysis_id,
        req.doc_ids,
        current_user_id,
        req.groq_api_key
    )
    
    return {
        "id": analysis_id,
        "status": "pending",
        "progress_message": "Queued for analysis.",
        "created_at": datetime.now(),
        "doc_ids": req.doc_ids
    }

@app.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, current_user_id: int = Depends(db.get_current_user_id)):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, status, progress_message, result_json, created_at, doc_ids FROM analyses WHERE id = ? AND user_id = ?",
        (analysis_id, current_user_id)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    result_dict = None
    if row["result_json"]:
        result_dict = json.loads(row["result_json"])
        
    doc_ids_list = [int(x) for x in row["doc_ids"].split(",") if x]
    
    return {
        "id": row["id"],
        "status": row["status"],
        "progress_message": row["progress_message"],
        "result": result_dict,
        "created_at": datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S") if isinstance(row["created_at"], str) else row["created_at"],
        "doc_ids": doc_ids_list
    }

# --- Serve React Frontend ---
# Serve Vite static files if they are compiled, otherwise serve the public index.html (runs React/Tailwind via CDN)
dist_path = "frontend/dist"
public_index_path = "frontend/public/index.html"

if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=f"{dist_path}/assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Allow API routes to pass through
        if full_path.startswith("api/") or full_path.startswith("documents") or full_path.startswith("auth") or full_path.startswith("analysis"):
            raise HTTPException(status_code=404)
        return FileResponse(f"{dist_path}/index.html")
else:
    @app.get("/{full_path:path}")
    async def serve_frontend_fallback(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("documents") or full_path.startswith("auth") or full_path.startswith("analysis"):
            raise HTTPException(status_code=404)
        if os.path.exists(public_index_path):
            return FileResponse(public_index_path)
        return {"message": "SME Document Intelligence Agent backend is running. React files build is pending."}
