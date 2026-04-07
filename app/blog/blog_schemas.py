from typing import Optional

from pydantic import BaseModel, Field

class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=128)
    content: str = Field(min_length=1)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=128)
    content: Optional[str] = Field(None, min_length=1)

class PostResponse(BaseModel):
    pass

class CommentCreate(BaseModel):
    content: str = Field(min_length=1)

class CommentResponse:
    pass