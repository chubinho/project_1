from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

from jose import jwt, JWTError
from passlib.hash import bcrypt

from datetime import datetime, timedelta, timezone
from typing import Annotated
from os import environ
from dotenv import load_dotenv

load_dotenv()


# JWT, Auth

SECRET_KEY = environ.get("SECRET_KEY", "notfound")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Database

engine = create_async_engine("sqlite+aiosqlite:///users.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str


async def get_session():
    async with new_session() as session:
        yield session


sessionDep = Annotated[AsyncSession, Depends(get_session)]


# Application


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)


# Endpoints


@app.post("/register")
async def register(user: UserRegister, session: sessionDep):
    existing = await session.scalar(select(User).where(User.email == user.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    new_user = User(email=user.email, password_hash=bcrypt.hash(user.password))
    session.add(new_user)
    await session.commit()

    return {"success": True, "message": "Пользователь зарегистрирован"}


@app.post("/login")
async def login(response: Response, data: UserLogin, session: sessionDep):
    user = await session.scalar(select(User).where(User.email == data.email))
    if not user or not bcrypt.verify(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    access_token = create_token(
        {"sub": str(user.id)}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        {"sub": str(user.id)}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {"success": True, "message": "Вход выполнен"}


@app.get("/refresh")
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Нет refresh токена")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный refresh токен")

    user_id = payload.get("sub")
    new_access = create_token(
        {"sub": user_id}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(key="access_token", value=new_access, httponly=True)

    return {"success": True, "message": "Access токен обновлён"}


@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"success": True, "message": "Вы вышли"}


@app.get("/me", response_model=UserOut)
async def get_me(request: Request, session: sessionDep):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Нет access токена")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Токен недействителен или истёк")

    user_id = payload.get("sub")
    user = await session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user
