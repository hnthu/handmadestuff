"""
models.py

Domain models for the Spaced Repetition app.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    """A flashcard with its answer."""

    id: int
    text: str
    answer: str


@dataclass(frozen=True)
class QuestionRow:
    """A question as displayed in the list view (includes schedule info)."""

    id: int
    text: str
    next_review: str  # ISO date string or 'N/A'
