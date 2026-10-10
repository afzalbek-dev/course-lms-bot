from typing import Dict, Any, Tuple
from .models import StudentProgress, Lesson
from .storage import LMSStorage


class LMSEngine:
    """O'quv kursi jarayonini nazorat qiluvchi dvigatel."""

    def __init__(self, storage: LMSStorage):
        self.storage = storage

    def get_current_lesson(self, user_id: int, course_id: str) -> Tuple[Lesson, StudentProgress]:
        progress = self.storage.get_progress(user_id, course_id)
        lesson = self.storage.get_lesson(course_id, progress.current_lesson_index)
        if not lesson:
            raise ValueError(f"Dars topilmadi: {course_id} #{progress.current_lesson_index}")
        return lesson, progress

    def submit_quiz_answer(
        self,
        user_id: int,
        course_id: str,
        question_index: int,
        selected_option: int,
    ) -> Dict[str, Any]:
        progress = self.storage.get_progress(user_id, course_id)
        lesson = self.storage.get_lesson(course_id, progress.current_lesson_index)
        if not lesson or not lesson.quiz:
            raise ValueError("Darsda test savollari mavjud emas")

        if not (0 <= question_index < len(lesson.quiz)):
            raise IndexError("Savol indeksi noto'g'ri")

        q = lesson.quiz[question_index]
        is_correct = (selected_option == q.correct_option_index)

        if is_correct:
            progress.total_quiz_score += 10

        # Faqat to'g'ri javob bo'lganda va oxirgi savol bo'lganda keyingi darsga o'tkazish
        if is_correct and question_index == len(lesson.quiz) - 1:
            if progress.current_lesson_index not in progress.completed_lessons:
                progress.completed_lessons.append(progress.current_lesson_index)

            # Keyingi dars bormi?
            next_lesson = self.storage.get_lesson(course_id, progress.current_lesson_index + 1)
            if next_lesson:
                progress.current_lesson_index += 1
            else:
                progress.is_completed = True

        self.storage.save_progress(progress)

        return {
            "is_correct": is_correct,
            "earned_points": 10 if is_correct else 0,
            "current_score": progress.total_quiz_score,
            "next_lesson_index": progress.current_lesson_index,
            "is_course_completed": progress.is_completed,
        }
