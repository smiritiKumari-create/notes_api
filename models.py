from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    Table, ForeignKey, Index,
)
from sqlalchemy.orm import relationship
from .database import Base

# ─── Association table (Note ↔ Tag) ──────────────────────────────────────────
note_tag_association = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id",  Integer, ForeignKey("tags.id",  ondelete="CASCADE"), primary_key=True),
)


# ─── Tag ──────────────────────────────────────────────────────────────────────
class Tag(Base):
    __tablename__ = "tags"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(64), unique=True, nullable=False, index=True)
    color      = Column(String(7), nullable=True)          # hex colour, e.g. "#3b82f6"
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # back-reference so Tag knows which notes use it
    notes = relationship(
        "Note",
        secondary=note_tag_association,
        back_populates="tags",
        lazy="select",
    )


# ─── Note ─────────────────────────────────────────────────────────────────────
class Note(Base):
    __tablename__ = "notes"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String(255), nullable=False)
    body         = Column(Text, nullable=False)       # raw Markdown stored here
    body_html    = Column(Text, nullable=True)        # rendered HTML (cached)
    is_pinned    = Column(Integer, default=0)         # 0 / 1 (MySQL has no BOOLEAN)
    created_at   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at   = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    tags = relationship(
        "Tag",
        secondary=note_tag_association,
        back_populates="notes",
        lazy="select",
    )

    # ── Full-text index on title + body (MySQL FULLTEXT) ──────────────────────
    __table_args__ = (
        Index(
            "ix_notes_fulltext",
            "title", "body",
            mysql_prefix="FULLTEXT",
        ),
    )