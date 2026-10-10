import sqlite3
import json
import time
from typing import List, Optional, Dict, Any
from .models import Course, Lesson, QuizQuestion, StudentProgress


class LMSStorage:
    """Kurslar, darslar va talabalar rivojlanishini SQLite bazasida saqlash."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS courses (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id TEXT NOT NULL,
                    order_index INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    quiz_json TEXT,
                    UNIQUE(course_id, order_index),
                    FOREIGN KEY(course_id) REFERENCES courses(id)
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS progress (
                    user_id INTEGER NOT NULL,
                    course_id TEXT NOT NULL,
                    current_lesson_index INTEGER DEFAULT 1,
                    completed_lessons_json TEXT,
                    total_quiz_score INTEGER DEFAULT 0,
                    is_completed INTEGER DEFAULT 0,
                    PRIMARY KEY(user_id, course_id)
                )
                """
            )

    def create_course(self, course_id: str, title: str, description: str):
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO courses (id, title, description) VALUES (?, ?, ?)",
                (course_id, title, description),
            )

    def add_lesson(self, course_id: str, order_index: int, title: str, content: str, quiz: List[QuizQuestion]) -> int:
        quiz_data = [
            {"question": q.question, "options": q.options, "correct_option_index": q.correct_option_index}
            for q in quiz
        ]
        with self._conn:
            cur = self._conn.execute(
                """
                INSERT INTO lessons (course_id, order_index, title, content, quiz_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (course_id, order_index, title, content, json.dumps(quiz_data)),
            )
            return cur.lastrowid

    def get_lesson(self, course_id: str, order_index: int) -> Optional[Lesson]:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT id, course_id, order_index, title, content, quiz_json FROM lessons WHERE course_id = ? AND order_index = ?",
            (course_id, order_index),
        )
        row = cur.fetchone()
        if not row:
            return None
        quiz_list = []
        if row[5]:
            for q in json.loads(row[5]):
                quiz_list.append(QuizQuestion(**q))
        return Lesson(row[0], row[1], row[2], row[3], row[4], quiz_list)

    def get_progress(self, user_id: int, course_id: str) -> StudentProgress:
        cur = self._conn.cursor()
        cur.execute(
            "SELECT user_id, course_id, current_lesson_index, completed_lessons_json, total_quiz_score, is_completed FROM progress WHERE user_id = ? AND course_id = ?",
            (user_id, course_id),
        )
        row = cur.fetchone()
        if not row:
            return StudentProgress(
                user_id=user_id,
                course_id=course_id,
                current_lesson_index=1,
                completed_lessons=[],
                total_quiz_score=0,
                is_completed=False,
            )
        completed = json.loads(row[3]) if row[3] else []
        return StudentProgress(
            user_id=row[0],
            course_id=row[1],
            current_lesson_index=row[2],
            completed_lessons=completed,
            total_quiz_score=row[4],
            is_completed=bool(row[5]),
        )

    def save_progress(self, progress: StudentProgress):
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO progress (user_id, course_id, current_lesson_index, completed_lessons_json, total_quiz_score, is_completed)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, course_id) DO UPDATE SET
                    current_lesson_index = excluded.current_lesson_index,
                    completed_lessons_json = excluded.completed_lessons_json,
                    total_quiz_score = excluded.total_quiz_score,
                    is_completed = excluded.is_completed
                """,
                (
                    progress.user_id,
                    progress.course_id,
                    progress.current_lesson_index,
                    json.dumps(progress.completed_lessons),
                    progress.total_quiz_score,
                    1 if progress.is_completed else 0,
                ),
            )

    def close(self):
        self._conn.close()
