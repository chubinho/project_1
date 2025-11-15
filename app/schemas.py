from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


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
    distincts: Optional[str] = None
    nickname: Optional[str] = None
    danger: Literal["danger", "safe", "unknown"]
    location: str
    geoLocation: str 
    time: str 
    contactName: str
    contactPhone: str
    contactEmail: EmailStr
    extras: Optional[str] = None
        
class AdOut(BaseModel):
    id: int
    status: str
    type: str
    breed: str
    color: str
    size: str
    distincts: Optional[str]
    nickname: Optional[str]
    danger: str
    location: str
    geoLocation: str
    time: str
    contactName: str
    contactPhone: str
    contactEmail: str
    extras: Optional[str]

    class Config:
        from_attributes = True

class UpdateName(BaseModel):
    name: str = Field(min_length=1,max_length=50)

class UpdateEmail(BaseModel):
    email: EmailStr

class UpdatePhone(BaseModel):
    phone: Optional[str] = Field(None, pattern=r"^\+7\d{10}$")

class UpdatePassword(BaseModel):
    curPassword: str = Field(..., min_length=8)
    newPassword: str = Field(..., min_length=8, max_length=72)