from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy import select
from jose import JWTError, jwt
from datetime import timedelta
from typing import Annotated
from ..dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
import random
from ..models import User
from ..schemas import UserRegister, UserLogin, UserOut, UpdateEmail, UpdateName, UpdatePhone, UpdatePassword
from ..database import get_session
from ..auth import create_token, verify_password, hash_password
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY, ALGORITHM

router = APIRouter()

sessionDep = Annotated[AsyncSession, Depends(get_session)]

names = ["Альфа", "Барсик", "Крош", "Стрелка", "Мурзик"]


@router.post("/register")
async def register(user: UserRegister, session: sessionDep):
    existing = await session.scalar(select(User).where(User.email == user.email))
    if existing:
        raise HTTPException(
            status_code=400, detail="Email уже зарегистрирован")

    user_name = user.name
    if not user_name:
        name = random.choice(names)
        num = random.randint(1, 999)
        user_name = f"{name}{num}"
    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        phone=user.phone,
        name=user_name,
        role="user",
    )
    session.add(new_user)
    await session.commit()

    return {"success": True, "message": "Пользователь зарегистрирован"}


@router.post("/login")
async def login(response: Response, data: UserLogin, session: sessionDep):
    user = await session.scalar(select(User).where(User.email == data.email))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=400, detail="Неверный email или пароль")

    access_token = create_token({"sub": str(user.id)}, timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_token(
        {"sub": str(user.id)}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token",
                        value=refresh_token, httponly=True)

    return {"success": True, "message": "Вход выполнен"}


@router.get("/refresh")
async def refresh_token(request: Request, response: Response):
    from jose import jwt

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Нет refresh токена")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Недействительный refresh токен")

    user_id = payload.get("sub")
    new_access = create_token({"sub": user_id}, timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie(key="access_token", value=new_access, httponly=True)

    return {"success": True, "message": "Access токен обновлён"}


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"success": True, "message": "Вы вышли"}


@router.get("/user")
async def get_user(request: Request, session: sessionDep):
    from jose import jwt

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Нет access токена")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Токен недействителен или истёк")

    user_id = payload.get("sub")
    user = await session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return {
        "user": {
            "name": user.name,
            "date": user.created_at.strftime("%d.%m.%Y"),
            "email": user.email,
            "phone": user.phone,
        }
    }

userDep = Annotated[User, Depends(get_current_user)]


@router.put("/user/name")
async def update_name(
    data: UpdateName,
    session: sessionDep,
    current_user: userDep
):
    current_user.name = data.name
    await session.commit()
    return {"success": True}


@router.put("/user/email")
async def update_email(
    data: UpdateEmail,
    session: sessionDep,
    current_user: userDep,
):
    existing = await session.scalar(
        select(User).where(User.email == data.email)
    )
    if existing and existing.id != current_user.id:
        return {"success": False, "message": "Email уже занят"}

    current_user.email = data.email
    await session.commit()
    return {"success": True}

@router.put("/user/phone")
async def update_phone(
    data: UpdatePhone,
    session: sessionDep,
    current_user: userDep
):
    current_user.phone = data.phone
    await session.commit()
    return {"success": True}

@router.put("/user/password")
async def update_password(
    data: UpdatePassword,
    session: sessionDep,
    current_user: userDep
):
    if not verify_password(data.curPassword, current_user.password_hash):
        return {"success": False, "message": "Неверный текущий пароль"}
    
    current_user.password_hash = hash_password(data.newPassword)
    await session.commit()
    return {"success": True}