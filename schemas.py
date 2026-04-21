from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import re


# ═══════════════════════════════════════════════════════════════════════════════
# Tag schemas
# ═══════════════════════════════════════════════════════════════════════════════

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, examples=["python"])
    color: Optional[str] = Field(None, examples=["#3b82f6"])

    @field_validator("name")
    @classmethod
    def slugify_name(cls, v: str) -> str:
        """Lowercase and replace spaces/special chars so tags are consistent."""
        return re.sub(r"[^\w-]", "-", v.strip().lower())

    @field_validator("color")
    @classmethod
    def validate_hex_color(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.fullmatch(r"#[0-9a-fA-F]{6}", v):
            raise ValueError("color must be a 6-digit hex code, e.g. #3b82f6")
        return v


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    name:  Optional[str] = Field(None, min_length=1, max_length=64)
    color: Optional[str] = None


class TagOut(TagBase):
    id:         int
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Note schemas
# ═══════════════════════════════════════════════════════════════════════════════

class NoteBase(BaseModel):
    title:     str  = Field(..., min_length=1, max_length=255, examples=["My First Note"])
    body:      str  = Field(..., min_length=1,                 examples=["# Hello\n\nThis is **markdown**."])
    is_pinned: bool = False


class NoteCreate(NoteBase):
    tag_ids: List[int] = Field(default_factory=list, examples=[[1, 2]])


class NoteUpdate(BaseModel):
    title:     Optional[str]       = Field(None, min_length=1, max_length=255)
    body:      Optional[str]       = Field(None, min_length=1)
    is_pinned: Optional[bool]      = None
    tag_ids:   Optional[List[int]] = None   # None = don't change; [] = remove all


class NoteOut(NoteBase):
    id:         int
    body_html:  Optional[str]
    tags:       List[TagOut]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════════
# Paginated list response
# ═══════════════════════════════════════════════════════════════════════════════

class PaginatedNotes(BaseModel):
    total:   int
    page:    int
    size:    int
    results: List[NoteOut]