"""
db.py

SQLite database layer for the Spaced Repetition app.
No UI dependencies.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from spaced_repetition.models import Question, QuestionRow

logger = logging.getLogger(__name__)

# Set by init_db(); all functions use this path.
_db_path: Path = Path("review_data.db")


def init_db(path: str | Path = "review_data.db") -> None:
    """Initialise the database and create tables if they don't exist.

    Args:
        path: Path to the SQLite database file. Stored for all subsequent calls.
    """
    global _db_path
    _db_path = Path(path)
    with sqlite3.connect(_db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS questions (
                id       INTEGER PRIMARY KEY,
                question TEXT    NOT NULL,
                answer   TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reviews (
                question_id INTEGER PRIMARY KEY,
                next_review DATE    NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );
        """)


def insert_question(question: str, answer: str) -> None:
    """Insert a new question/answer pair."""
    with sqlite3.connect(_db_path) as conn:
        conn.execute(
            "INSERT INTO questions (question, answer) VALUES (?, ?)",
            (question, answer),
        )


def delete_question(question_id: int | str) -> None:
    """Delete a question and its review schedule by ID."""
    with sqlite3.connect(_db_path) as conn:
        conn.execute("DELETE FROM reviews  WHERE question_id = ?", (question_id,))
        conn.execute("DELETE FROM questions WHERE id = ?",          (question_id,))
    logger.info("Deleted question id=%s", question_id)


def load_due_questions() -> list[Question]:
    """Return questions due for review today (or never reviewed)."""
    today = date.today()
    with sqlite3.connect(_db_path) as conn:
        rows = conn.execute(
            """SELECT q.id, q.question, q.answer
               FROM questions q
               LEFT JOIN reviews r ON q.id = r.question_id
               WHERE r.next_review <= ? OR r.next_review IS NULL""",
            (today,),
        ).fetchall()
    return [Question(id=r[0], text=r[1], answer=r[2]) for r in rows]


def load_all_with_schedule() -> list[QuestionRow]:
    """Return all questions with their next review date for the list view."""
    with sqlite3.connect(_db_path) as conn:
        rows = conn.execute(
            """SELECT q.id, q.question, IFNULL(r.next_review, 'N/A')
               FROM questions q
               LEFT JOIN reviews r ON q.id = r.question_id"""
        ).fetchall()
    return [QuestionRow(id=r[0], text=r[1], next_review=r[2]) for r in rows]


def update_schedule(question_id: int, correct: bool) -> None:
    """Update the next review date based on whether the answer was correct.

    Correct answers are scheduled 7 days out; incorrect answers 1 day out.
    """
    days = 7 if correct else 1
    next_review = date.today() + timedelta(days=days)
    with sqlite3.connect(_db_path) as conn:
        conn.execute(
            "REPLACE INTO reviews (question_id, next_review) VALUES (?, ?)",
            (question_id, next_review),
        )
