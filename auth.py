"""
Authentication utilities: password hashing, JWT token generation, role-based access control
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pydantic import BaseModel

# Use Argon2 for password hashing (supports unlimited password length)
hasher = PasswordHasher()

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours



# ============================================================================
# SCHEMAS FOR API REQUESTS/RESPONSES
# ============================================================================

class UserRegister(BaseModel):
    """Registration request"""
    email: str
    full_name: str
    password: str
    role: str  # "patient" or "doctor"


class UserLogin(BaseModel):
    """Login request"""
    email: str
    password: str


class UserResponse(BaseModel):
    """User response without password"""
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    user: UserResponse


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a plain password using Argon2 (supports unlimited password length)"""
    return hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        hasher.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False



# ============================================================================
# JWT TOKEN GENERATION & VALIDATION
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None


# ============================================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================================

class RoleRequired:
    """Dependency to check user role"""
    def __init__(self, required_roles: list[str]):
        self.required_roles = required_roles
    
    def __call__(self, token: str) -> dict:
        payload = verify_token(token)
        if not payload:
            raise Exception("Invalid token")
        
        user_role = payload.get("role")
        if user_role not in self.required_roles:
            raise Exception(f"Requires one of roles: {self.required_roles}")
        
        return payload
