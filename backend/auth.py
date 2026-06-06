from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import select
from core.database import Base, async_session
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int, email: str, name: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "name": name,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def create_user(name: str, email: str, password: str) -> dict:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            return {"error": "Email already registered"}

        user = User(
            name=name,
            email=email,
            hashed_password=hash_password(password)
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_token(user.id, user.email, user.name)
        return {"token": token, "user": {"name": user.name, "email": user.email}}


async def login_user(email: str, password: str) -> dict:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            return {"error": "Invalid email or password"}

        token = create_token(user.id, user.email, user.name)
        return {"token": token, "user": {"name": user.name, "email": user.email}}