from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at :datetime

    class Config:
        orm_mode = True


class Post(BaseModel):
    id: int
    title : str
    content: str
    published: bool
    created_at: datetime
    owner_id : int
    owner : UserOut

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr 
    password: str



class Userlogin(BaseModel):
    email : EmailStr
    password : str

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    
    id: str|None = None
    # id : Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1) # type: ignore

    class Config:
        orm_mode = True


class GetPost(BaseModel):
    

    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner_id : int

    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post:GetPost
    votes:int

    class Config:
        orm_mode = True