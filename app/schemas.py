from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    phone: Optional[str] = Field(None,pattern= r"^\+?[1-9]\d{1,14}$")
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    date: str

    class Config:
        from_attributes = True
