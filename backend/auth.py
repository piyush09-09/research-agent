from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from sqlalchemy import Column, Integer, String, DateTime, Text, Float,ForeignKey
from sqlalchemy import select
from core.database import Base, async_session
from core.config import settings
import bcrypt

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

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    query = Column(String, nullable=False)
    word_limit = Column(Integer, default=500)
    report = Column(Text, nullable=False)
    faithfulness = Column(Float, nullable=True)
    answer_relevancy = Column(Float, nullable=True)
    context_precision = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


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
    

async def save_session(user_id: int, query: str, word_limit: int, report: str, eval_scores: dict) -> dict:
    async with async_session() as session:
        research = ResearchSession(
            user_id=user_id,
            query=query,
            word_limit=word_limit,
            report=report,
            faithfulness=eval_scores.get("faithfulness"),
            answer_relevancy=eval_scores.get("answer_relevancy"),
            context_precision=eval_scores.get("context_precision"),
            overall_score=eval_scores.get("overall"),
        )
        session.add(research)
        await session.commit()
        await session.refresh(research)
        return {"id": research.id, "query": research.query, "created_at": str(research.created_at)}


async def get_user_history(user_id: int) -> list:
    async with async_session() as session:
        result = await session.execute(
            select(ResearchSession)
            .where(ResearchSession.user_id == user_id)
            .order_by(ResearchSession.created_at.desc())
            .limit(50)
        )
        sessions = result.scalars().all()
        return [
            {
                "id": s.id,
                "query": s.query,
                "word_limit": s.word_limit,
                "report": s.report,
                "eval_scores": {
                    "faithfulness": s.faithfulness,
                    "answer_relevancy": s.answer_relevancy,
                    "context_precision": s.context_precision,
                    "overall": s.overall_score,
                },
                "created_at": str(s.created_at),
            }
            for s in sessions
        ]


async def get_session_by_id(session_id: int, user_id: int) -> dict | None:
    async with async_session() as session:
        result = await session.execute(
            select(ResearchSession).where(
                ResearchSession.id == session_id,
                ResearchSession.user_id == user_id
            )
        )
        s = result.scalar_one_or_none()
        if not s:
            return None
        return {
            "id": s.id,
            "query": s.query,
            "word_limit": s.word_limit,
            "report": s.report,
            "eval_scores": {
                "faithfulness": s.faithfulness,
                "answer_relevancy": s.answer_relevancy,
                "context_precision": s.context_precision,
                "overall": s.overall_score,
            },
            "created_at": str(s.created_at),
        }


async def delete_session(session_id: int, user_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(ResearchSession).where(
                ResearchSession.id == session_id,
                ResearchSession.user_id == user_id
            )
        )
        research = result.scalar_one_or_none()
        if not research:
            return False
        await session.delete(research)
        await session.commit()
        return True