import uuid
from pydantic import BaseModel, EmailStr
from app.schemas.user import UserResponse


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str  = None
    exp: int  = None


class Login(BaseModel):
    email: EmailStr
    password: str


class Msg(BaseModel):
    msg: str
