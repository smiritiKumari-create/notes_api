from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/notes", tags=["Notes"])


# ── GET /notes ────────────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=schemas.PaginatedNotes,
    summary="List / search notes",
    description="""
Returns a paginated list of notes.

**Query parameters:**

| Param       | Type     | Description |
|-------------|----------|-------------|
| `search`    | string   | Full-text search across title and body |
| `tags`      | string[] | Filter by one or more tag names (AND logic) |
| `is_pinned` | bool     | Filter pinned / unpinned notes |
| `page`      | int ≥ 1  | Page number (default 1) |
| `size`      | int 1-100| Items per page (default 20) |
""",
)
def list_notes(
    search:    Optional[str]        = Query(None,  description="Full-text search query"),
    tags:      Optional[List[str]]  = Query(None,  description="Filter by tag name(s)"),
    is_pinned: Optional[bool]       = Query(None,  description="Filter by pinned status"),
    page:      int                  = Query(1,     ge=1,       description="Page number"),
    size:      int                  = Query(20,    ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    total, notes = crud.list_notes(
        db,
        search=search,
        tag_names=tags,
        is_pinned=is_pinned,
        page=page,
        size=size,
    )
    return schemas.PaginatedNotes(total=total, page=page, size=size, results=notes)


# ── POST /notes ───────────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=schemas.NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
)
def create_note(payload: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db, payload)


# ── GET /notes/{note_id} ──────────────────────────────────────────────────────
@router.get("/{note_id}", response_model=schemas.NoteOut, summary="Get a note by ID")
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return note


# ── PATCH /notes/{note_id} ────────────────────────────────────────────────────
@router.patch("/{note_id}", response_model=schemas.NoteOut, summary="Update a note")
def update_note(note_id: int, payload: schemas.NoteUpdate, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return crud.update_note(db, note, payload)


# ── DELETE /notes/{note_id} ───────────────────────────────────────────────────
@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    crud.delete_note(db, note)


# ── GET /notes/{note_id}/rendered ────────────────────────────────────────────
@router.get(
    "/{note_id}/rendered",
    summary="Get rendered HTML for a note",
    response_model=dict,
)
def get_rendered_note(note_id: int, db: Session = Depends(get_db)):
    """Returns the pre-rendered HTML body of a note."""
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return {"id": note.id, "title": note.title, "body_html": note.body_html}