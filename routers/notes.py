from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

import crud, schemas
from database import get_db

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("/", response_model=schemas.PaginatedNotes)
def list_notes(
    search:    Optional[str]        = Query(None),
    tags:      Optional[List[str]]  = Query(None),
    is_pinned: Optional[bool]       = Query(None),
    page:      int                  = Query(1, ge=1),
    size:      int                  = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total, notes = crud.list_notes(db, search=search, tag_names=tags, is_pinned=is_pinned, page=page, size=size)
    return schemas.PaginatedNotes(total=total, page=page, size=size, results=notes)


@router.post("/", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(payload: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db, payload)


@router.get("/{note_id}", response_model=schemas.NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return note


@router.patch("/{note_id}", response_model=schemas.NoteOut)
def update_note(note_id: int, payload: schemas.NoteUpdate, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return crud.update_note(db, note, payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    crud.delete_note(db, note)


@router.get("/{note_id}/rendered", response_model=dict)
def get_rendered_note(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return {"id": note.id, "title": note.title, "body_html": note.body_html}