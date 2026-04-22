"""
crud.py
-------
All database operations for Notes and Tags.
Kept separate from route handlers so business logic is easy to test.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, text
from sqlalchemy.orm import Session

import models, schemas
from markdown_utils import render_markdown


# ═══════════════════════════════════════════════════════════════════════════════
# Tag CRUD
# ═══════════════════════════════════════════════════════════════════════════════

def get_tag(db: Session, tag_id: int) -> Optional[models.Tag]:
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()


def get_tag_by_name(db: Session, name: str) -> Optional[models.Tag]:
    return db.query(models.Tag).filter(models.Tag.name == name).first()


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tag]:
    return db.query(models.Tag).offset(skip).limit(limit).all()


def create_tag(db: Session, payload: schemas.TagCreate) -> models.Tag:
    tag = models.Tag(**payload.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def update_tag(db: Session, tag: models.Tag, payload: schemas.TagUpdate) -> models.Tag:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(tag, field, value)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag: models.Tag) -> None:
    db.delete(tag)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# Note CRUD
# ═══════════════════════════════════════════════════════════════════════════════

def get_note(db: Session, note_id: int) -> Optional[models.Note]:
    return db.query(models.Note).filter(models.Note.id == note_id).first()


def _apply_tag_ids(db: Session, note: models.Note, tag_ids: List[int]) -> None:
    """Replace a note's tag list with the supplied tag IDs."""
    tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all()
    note.tags = tags


def create_note(db: Session, payload: schemas.NoteCreate) -> models.Note:
    data = payload.model_dump(exclude={"tag_ids"})
    data["body_html"] = render_markdown(data["body"])
    note = models.Note(**data)
    db.add(note)
    db.flush()                                    # get note.id before associating tags
    _apply_tag_ids(db, note, payload.tag_ids)
    db.commit()
    db.refresh(note)
    return note


def update_note(db: Session, note: models.Note, payload: schemas.NoteUpdate) -> models.Note:
    data = payload.model_dump(exclude_unset=True, exclude={"tag_ids"})

    # Re-render HTML only when the body actually changed
    if "body" in data:
        data["body_html"] = render_markdown(data["body"])

    for field, value in data.items():
        setattr(note, field, value)

    if payload.tag_ids is not None:
        _apply_tag_ids(db, note, payload.tag_ids)

    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note: models.Note) -> None:
    db.delete(note)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# Listing & searching notes
# ═══════════════════════════════════════════════════════════════════════════════

def list_notes(
    db: Session,
    *,
    search:    Optional[str] = None,
    tag_names: Optional[List[str]] = None,
    is_pinned: Optional[bool] = None,
    page:      int = 1,
    size:      int = 20,
) -> Tuple[int, List[models.Note]]:
    """
    Return (total_count, notes_page).

    Filtering options:
      • search    – MySQL FULLTEXT MATCH…AGAINST on title + body
      • tag_names – notes must have ALL of the supplied tags
      • is_pinned – True / False / None (all)
    """
    q = db.query(models.Note)

    # ── Full-text search ──────────────────────────────────────────────────────
    if search:
        ft_expr = text(
            "MATCH(notes.title, notes.body) AGAINST (:q IN BOOLEAN MODE)"
        ).bindparams(q=search)
        q = q.filter(ft_expr)

    # ── Tag filter (note must carry every requested tag) ──────────────────────
    if tag_names:
        for name in tag_names:
            q = q.filter(
                models.Note.tags.any(
                    func.lower(models.Tag.name) == name.lower()
                )
            )

    # ── Pinned filter ─────────────────────────────────────────────────────────
    if is_pinned is not None:
        q = q.filter(models.Note.is_pinned == (1 if is_pinned else 0))

    # ── Ordering: pinned first, then newest first ─────────────────────────────
    q = q.order_by(models.Note.is_pinned.desc(), models.Note.updated_at.desc())

    total  = q.count()
    offset = (page - 1) * size
    notes  = q.offset(offset).limit(size).all()

    return total, notes