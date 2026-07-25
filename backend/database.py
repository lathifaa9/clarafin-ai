import os
import sqlite3
import jwt
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

# Authentication configuration must be loaded before SECRET_KEY is evaluated.
# Otherwise every reload falls back to a newly generated key, invalidating
# browser tokens while users are uploading files.
load_dotenv()

DB_FILE = "finance_agent.db"
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_urlsafe(48))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create Documents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        file_size INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Create Analyses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        progress_message TEXT NOT NULL,
        result_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        doc_ids TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    conn.commit()
    
    # Seed a Demo User for the hackathon judges
    try:
        demo_email = "demo@sme-agent.com"
        cursor.execute("SELECT id FROM users WHERE email = ?", (demo_email,))
        if not cursor.fetchone():
            hashed_pw = pwd_context.hash("demo1234")
            cursor.execute("INSERT INTO users (email, hashed_password) VALUES (?, ?)", (demo_email, hashed_pw))
            conn.commit()
            print("Seeded demo user: demo@sme-agent.com / demo1234")
    except Exception as e:
        print(f"Error seeding demo user: {e}")
        
    conn.close()

# --- Auth Helpers ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "email": email, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": str(user_id), "email": email, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security_scheme)) -> int:
    payload = verify_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token required")
    return int(payload.get("sub"))
