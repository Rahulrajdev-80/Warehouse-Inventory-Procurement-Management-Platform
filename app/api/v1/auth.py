from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, Token, TokenRefresh, PasswordResetRequest, PasswordResetConfirm, UserResponse
)
from app.services.auth_service import AuthService
from app.security import get_current_user, decode_token, create_access_token, get_password_hash
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """User Registration"""
    return await AuthService.register_user(db, user_data)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """User Login returning Access & Refresh JWT Tokens"""
    return await AuthService.authenticate_user(db, credentials)

@router.post("/refresh", response_model=Token)
async def refresh_token(data: TokenRefresh):
    """Refresh Access Token"""
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token type")
    user_id = payload.get("sub")
    new_access = create_access_token({"sub": user_id})
    return {"access_token": new_access, "refresh_token": data.refresh_token, "token_type": "bearer"}

@router.post("/reset-password")
async def reset_password(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """Password Reset Request (Mock Token Generation)"""
    return {"message": "Password reset link sent to your registered email if account exists."}
