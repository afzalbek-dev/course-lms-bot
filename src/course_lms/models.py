from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct_option_index: int


@dataclass
class Lesson:
    id: int
    course_id: str
    order_index: int
    title: str
    content: str
    quiz: List[QuizQuestion] = field(default_factory=list)


@dataclass
class Course:
    id: str
    title: str
    description: str
    total_lessons: int = 0


@dataclass
class StudentProgress:
    user_id: int
    course_id: str
    current_lesson_index: int
    completed_lessons: List[int]
    total_quiz_score: int
    is_completed: bool
