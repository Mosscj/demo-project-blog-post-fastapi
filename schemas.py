from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None

class CommentOut(BaseModel):
    id: int
    content: str
    timestamp: datetime
    post_id: int
    owner_id: int
    parent_id: Optional[int]
    replies: List["CommentOut"] = []

    class Config:
        from_attributes = True

CommentOut.update_forward_refs()