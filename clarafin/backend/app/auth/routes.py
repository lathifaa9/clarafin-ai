import sqlite3
from fastapi import APIRouter, HTTPException, status
from clarafin.backend.app.auth.models import UserCreate, UserResponse, LoginRequest, TokenResponse
import clarafin.backend.app.db.session as session

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate):
    conn = session.get_db_connection()
    cursor = conn.cursor()
    try:
        hashed_pw = session.hash_password(user_data.password)
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

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    conn = session.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, hashed_password FROM users WHERE email = ?", (login_data.email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not session.verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    access = session.create_access_token(user["id"], user["email"])
    refresh = session.create_refresh_token(user["id"], user["email"])
    return {"access_token": access, "refresh_token": refresh}
