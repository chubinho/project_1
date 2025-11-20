from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String, Text, ForeignKey, ARRAY, Integer
from database import Base
from datetime import datetime, timezone
from typing import Optional


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    phone: Mapped[Optional[str]] = mapped_column(default="")
    name: Mapped[Optional[str]] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(default="user")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    status: Mapped[str] = mapped_column(String(10))
    type: Mapped[str] = mapped_column(String(10))
    breed: Mapped[str] = mapped_column(String(30))
    color: Mapped[str] = mapped_column(String(20))
    size: Mapped[str] = mapped_column(String(10))
    distincts: Mapped[str] = mapped_column(Text, default='')
    nickname: Mapped[str] = mapped_column(String(50), default='')
    danger: Mapped[str] = mapped_column(String(10))
    location: Mapped[str] = mapped_column(String(100), default='')
    geoLocation: Mapped[ARRAY[int]] = mapped_column(ARRAY(Integer, as_tuple=True), default=[])
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    contactName: Mapped[str] = mapped_column(String(50))
    contactPhone: Mapped[str] = mapped_column(String(20))
    contactEmail: Mapped[str] = mapped_column(String(100))
    extras: Mapped[str] = mapped_column(Text, default='')

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
