from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

class PostCreate(BaseModel):
    title: str = Field(min_length=3, max_length=128)
    content: str = Field(min_length=1)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=128)
    content: Optional[str] = Field(None, min_length=1)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "PostUpdate":
        if self.title is None and self.content is None:
            raise ValueError("At least one field must be provided.")
        return self


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)

class CommentResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    comments: list[CommentResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)