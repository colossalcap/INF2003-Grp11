"""
Authentication API — JWT + bcrypt + Role-Based Access Control.
===============================================================

Stateless auth using JSON Web Tokens (HMAC-SHA256). Passwords hashed with
bcrypt (passlib) — deliberately slow to resist brute-force attacks.

SECURITY:
  - bcrypt hashing with auto-upgrade (passlib CryptContext)
  - JWT with configurable expiry (default 60 min)
  - Role-based access: customer vs admin
  - OAuth2PasswordBearer token flow
  - Sub claim as string (python-jose rejects integer sub values)

ENDPOINTS:
  POST /api/auth/register — Create account → bcrypt hash → PG users table
  POST /api/auth/login    — Authenticate → return JWT access_token
  GET  /api/auth/me       — Return current user from token payload
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.relational import get_db, User, Customer
from config import settings

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Pydantic models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    display_name: Optional[str] = None

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    display_name: Optional[str]
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ------------------------------------------------------------
# JWT Helpers
# ------------------------------------------------------------
def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode JWT and return the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return current_user


# ------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------
@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Validate input
    if not user_data.username or len(user_data.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if not user_data.email or '@' not in user_data.email or '.' not in user_data.email.split('@')[-1]:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    # Check uniqueness
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken.")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Create user
    hashed = pwd_context.hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed,
        display_name=user_data.display_name or user_data.username,
        role="customer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-create a Customer record linked to this user for order placement
    import uuid
    customer = Customer(
        customer_id=str(uuid.uuid4()),
        country_code="XX",
        opt_in_status=True,
    )
    db.add(customer)
    db.commit()

    # Generate token (sub must be a string for python-jose)
    token = create_access_token({"sub": str(user.user_id)})

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    token = create_access_token({"sub": str(user.user_id)})

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            role=user.role,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's profile."""
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        role=current_user.role,
    )
