from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    UserName: str = Field(..., min_length=2, max_length=50)
    Email: EmailStr
    Password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    Email: EmailStr
    Password: str

class UserResponse(BaseModel):
    UserID: int
    UserName: str
    Email: EmailStr
    CreatedAt: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr | None = None
    user_id: int | None = None
