from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime
from .database import Base
from datetime import datetime
from typing import Optional

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    phone: Mapped[Optional[str]] = mapped_column(nullable=True)
    name: Mapped[Optional[str]] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=datetime.utcnow,nullable=False)