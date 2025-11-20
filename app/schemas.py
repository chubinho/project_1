from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, List
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    phone: Optional[str] = Field(None,pattern= r"^\+7\d{10}$")
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

class AdCreate(BaseModel):
    status: Literal["lost", "found"]
    type: Literal["dog", "cat"]
    breed: Literal["labrador", "german_shepherd", "poodle", "metis"]
    color: str
    size: Literal["little", "medium", "big"]
    distincts: str = ''
    nickname: str = ''
    danger: Literal["danger", "safe", "unknown"]
    location: str = ''
    geoLocation: List[str] = []
    time: str
    contactName: str
    contactPhone: str
    contactEmail: EmailStr
    extras: str = ''
        
class AdOut(BaseModel):
    id: int
    status: str
    type: str
    breed: str
    color: str
    size: str
    distincts: str = ''
    nickname: str = ''
    danger: str
    location: str = ''
    geoLocation: List[str] = []
    time: datetime
    contactName: str
    contactPhone: str
    contactEmail: str
    extras: str = ''

    class Config:
        from_attributes = True

class AdFilters(BaseModel):
    status: Optional[str] = None
    type: Optional[str] = None
    breed: Optional[str] = None
    size: Optional[str] = None
    danger: Optional[str] = None

class UpdateName(BaseModel):
    name: str = Field(min_length=1,max_length=50)

class UpdateEmail(BaseModel):
    email: EmailStr

class UpdatePhone(BaseModel):
    phone: str = Field(None, pattern=r"^\+7\d{10}$")

class UpdatePassword(BaseModel):
    curPassword: str = Field(..., min_length=8)
    newPassword: str = Field(..., min_length=8, max_length=72)