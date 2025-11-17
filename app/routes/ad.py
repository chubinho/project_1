from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Annotated
from datetime import datetime

from dependencies import get_current_user
from database import get_session
from models import Ad, User
from schemas import AdOut, AdCreate

router = APIRouter()
sessionDep = Annotated[AsyncSession, Depends(get_session)]
userDep = Annotated[User, Depends(get_current_user)]

@router.post("/ads/create")
async def create_ad(data: AdCreate, session: sessionDep, current_user: userDep):
    try:
        time_obj = datetime.strptime(data.time, "%d.%m.%Y %H:%M")
    except ValueError:
        return {"success": False, "message": "Неверный формат времени"}

    ad = Ad(
        user_id=current_user.id,
        status=data.status,
        type=data.type,
        breed=data.breed,
        color=data.color,
        size=data.size,
        distincts=data.distincts,
        nickname=data.nickname,
        danger=data.danger,
        location=data.location,
        geoLocation=data.geoLocation,
        time=time_obj,
        contactName=data.contactName,
        contactPhone=data.contactPhone,
        contactEmail=data.contactEmail,
        extras=data.extras
    )

    session.add(ad)
    await session.commit()
    await session.refresh(ad)

    return {"success": True, "ad_id": ad.id}

@router.post("/ads/get")
async def get_ads(
    status: Optional[str] = None,
    type: Optional[str] = None,
    breed: Optional[str] = None,
    size: Optional[str] = None,
    danger: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    try:
        query = select(Ad)

        if status:
            query = query.where(Ad.status == status)
        if type:
            query = query.where(Ad.type == type)
        if breed:
            query = query.where(Ad.breed == breed)
        if size:
            query = query.where(Ad.size == size)
        if danger:
            query = query.where(Ad.danger == danger)

        query = query.order_by(Ad.created_at.desc()).limit(50)

        result = await session.scalars(query)
        ads = result.all()

        ads_out = [AdOut.model_validate(ad) for ad in ads]

        return {"success": True, "ads": ads_out}

    except Exception as e:
        print("Ошибка в /ads:", e)
        return {"success": False, "message": "Ошибка на сервере"}
