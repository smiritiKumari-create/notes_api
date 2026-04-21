from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from database import get_db

router = APIRouter(prefix="/tags", tags=["Tags"])


# ── GET /tags ─────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[schemas.TagOut], summary="List all tags")
def list_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tags(db, skip=skip, limit=limit)


# ── POST /tags ────────────────────────────────────────────────────────────────
@router.post("/", response_model=schemas.TagOut, status_code=status.HTTP_201_CREATED,
             summary="Create a new tag")
def create_tag(payload: schemas.TagCreate, db: Session = Depends(get_db)):
    existing = crud.get_tag_by_name(db, payload.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag '{payload.name}' already exists (id={existing.id}).",
        )
    return crud.create_tag(db, payload)


# ── GET /tags/{tag_id} ────────────────────────────────────────────────────────
@router.get("/{tag_id}", response_model=schemas.TagOut, summary="Get a tag by ID")
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = crud.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")
    return tag


# ── PATCH /tags/{tag_id} ──────────────────────────────────────────────────────
@router.patch("/{tag_id}", response_model=schemas.TagOut, summary="Update a tag")
def update_tag(tag_id: int, payload: schemas.TagUpdate, db: Session = Depends(get_db)):
    tag = crud.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")
    return crud.update_tag(db, tag, payload)


# ── DELETE /tags/{tag_id} ─────────────────────────────────────────────────────
@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a tag")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = crud.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")
    crud.delete_tag(db, tag)