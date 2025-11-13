from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Annotated
from ..database import get_session
from ..models import Ad
from ..schemas import AdOut

router = APIRouter()
sessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/ads")
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
