from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from services.openai_service import generate_health_summary
from database import init_db, get_db, User, SessionLocal
from auth import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    hash_password, verify_password, create_access_token, verify_token
)
from sqlalchemy.orm import Session
import os

load_dotenv()

# Initialize database
init_db()

app = FastAPI(title="Smart EHR Summarizer", version="1.1.0")

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    os.makedirs("static", exist_ok=True)


# ============================================================================
# HEALTH CHECK & ROOT
# ============================================================================

@app.get("/")
def root():
    """Serve landing page"""
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "OK", "version": "1.1.0"}


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/register", response_model=UserResponse)
def register(request: UserRegister, db: Session = Depends(get_db)):
    """Register new user (patient or doctor)"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate role
    if request.role not in ["patient", "doctor"]:
        raise HTTPException(status_code=400, detail="Role must be 'patient' or 'doctor'")
    
    # Create new user
    user = User(
        email=request.email,
        full_name=request.full_name,
        password_hash=hash_password(request.password),
        role=request.role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@app.post("/auth/login", response_model=TokenResponse)
def login(request: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    # Create JWT token
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@app.get("/auth/verify")
def verify_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Verify JWT token and return current user"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# ============================================================================
# ORIGINAL SUMMARIZE ENDPOINT (with auth)
# ============================================================================

@app.post("/summarize")
def summarize(payload: dict, authorization: str = Header(None), db: Session = Depends(get_db)):
    """Summarize medical text (requires authentication)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Extract and verify token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    payload_data = verify_token(token)
    if not payload_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    if "text" not in payload:
        raise HTTPException(status_code=400, detail="Missing medical text")
    
    return generate_health_summary(payload["text"])
