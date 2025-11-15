from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Annotated
from datetime import datetime
from math import radians, sin, asin, sqrt, cos

from ..dependencies import get_current_user
from ..database import get_session
from ..models import Ad, User
from ..schemas import AdOut, AdCreate

router = APIRouter()
sessionDep = Annotated[AsyncSession, Depends(get_session)]
userDep = Annotated[User, Depends(get_current_user)]


@router.post("/ads")
async def create_ad(data: AdCreate, session: sessionDep, current_user: userDep):
    try:
        time_obj = datetime.strptime(data.time, "%d.%m.%Y %H:%M:%S")
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


def haversine(lat1, lon1, lat2, lon2):
    """Вычисление расстояния между двумя точками"""
    R = 6371
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


@router.get("/ads")
async def get_ads(
    status: Optional[str] = None,
    type: Optional[str] = None,
    breed: Optional[str] = None,
    size: Optional[str] = None,
    danger: Optional[str] = None,
    region: Optional[str] = None,
    geoloc: Optional[str] = "any",
    radius: Optional[int] = None,
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
        filtered_ads = []
        if geoloc != "any":
            try:
                user_lat, user_lon = map(float, geoloc.split(","))
            except:
                return {"success": False, "message": "Неверный формат geoloc"}

            for ad in ads:
                if not ad.geoLocation:
                    continue

                try:
                    ad_lat, ad_lon = map(float, ad.geoLocation.split(","))
                except:
                    continue

                distance = haversine(user_lat, user_lon, ad_lat, ad_lon)

                if radius is None or distance <= radius:
                    filtered_ads.append(ad)
        else:
            if region:
                for ad in ads:
                    if ad.location and region.lower() in ad.location.lower():
                        filtered_ads.append(ad)
            else:
                filtered_ads = []
        ads_out = [AdOut.model_validate(ad) for ad in filtered_ads]

        return {"success": True, "ads": ads_out}

    except Exception as e:
        print("Ошибка в /ads:", e)
        return {"success": False, "message": "Ошибка на сервере"}
