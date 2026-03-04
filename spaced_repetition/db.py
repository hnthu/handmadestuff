"""
db.py

SQLite database layer for the Spaced Repetition app.
No UI dependencies.
"""

import logging
import sqlite3
from datetime import date, timedelta

DATABASE_FILE = 'review_data.db'

logger = logging.getLogger(__name__)


def _execute(cursor, query, params=None):
    logger.info("SQL: %s | params: %s", query, params)
    cursor.execute(query, params or ())


def init_db():
    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS questions
                     (id INTEGER PRIMARY KEY, question TEXT, answer TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS reviews
                     (question_id INTEGER, next_review DATE,
                      FOREIGN KEY(question_id) REFERENCES questions(id))''')
        conn.commit()


def insert_question(question, answer):
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (question, answer))
        conn.commit()


def delete_question(question_id):
    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        _execute(c, "DELETE FROM reviews WHERE question_id = ?", (question_id,))
        _execute(c, "DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()


def load_due_questions():
    """Return questions due for review today (or never reviewed)."""
    today = date.today()
    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT q.id, q.question, q.answer
                     FROM questions q
                     LEFT JOIN reviews r ON q.id = r.question_id
                     WHERE r.next_review <= ? OR r.next_review IS NULL''', (today,))
        return c.fetchall()


def load_all_with_schedule():
    """Return all questions with their next review date (or 'N/A')."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT id, question, IFNULL(next_review, 'N/A')
                     FROM questions
                     LEFT JOIN reviews ON questions.id = reviews.question_id''')
        return c.fetchall()


def update_schedule(question_id, correct):
    days = 7 if correct else 1
    next_review = date.today() + timedelta(days=days)
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.execute("REPLACE INTO reviews (question_id, next_review) VALUES (?, ?)",
                     (question_id, next_review))
        conn.commit()
