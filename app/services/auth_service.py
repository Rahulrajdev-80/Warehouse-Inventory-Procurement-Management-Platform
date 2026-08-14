from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserLogin
from app.security import get_password_hash, verify_password, create_access_token, create_refresh_token

class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, data: UserRegister) -> User:
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="User with this email already exists")

        new_user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            role=data.role or UserRole.INVENTORY_STAFF,
            warehouse_id=data.warehouse_id
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, data: UserLogin) -> dict:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalars().first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="User account is inactive")

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
