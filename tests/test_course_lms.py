import pytest
from course_lms.models import QuizQuestion
from course_lms.storage import LMSStorage
from course_lms.engine import LMSEngine


def test_lms_flow_progression(tmp_path):
    db_file = str(tmp_path / "lms_test.db")
    storage = LMSStorage(db_file)
    engine = LMSEngine(storage)

    # Kurs va darslar yaratish
    storage.create_course("fastapi", "FastAPI Kursi", "Zamonaviy backend")
    q1 = QuizQuestion("FastAPIda marshrut decorator?", ["@app.get", "@app.route", "@router"], 0)
    storage.add_lesson("fastapi", 1, "Routing", "Asosiy marshrutlar", [q1])

    q2 = QuizQuestion("Pydantic nima uchun?", ["CSS uchun", "Validatsiya uchun", "Docker uchun"], 1)
    storage.add_lesson("fastapi", 2, "Pydantic Models", "Sxemalarni tekshirish", [q2])

    user_id = 999
    # 1. Boshlang'ich holat
    lesson, progress = engine.get_current_lesson(user_id, "fastapi")
    assert lesson.order_index == 1
    assert progress.total_quiz_score == 0

    # 2. Noto'g'ri javob
    res1 = engine.submit_quiz_answer(user_id, "fastapi", question_index=0, selected_option=2)
    assert res1["is_correct"] is False
    assert res1["current_score"] == 0

    # 3. To'g'ri javob -> 2-darsga o'tish
    res2 = engine.submit_quiz_answer(user_id, "fastapi", question_index=0, selected_option=0)
    assert res2["is_correct"] is True
    assert res2["current_score"] == 10
    assert res2["next_lesson_index"] == 2

    # 4. 2-dars testini topshirish -> Kursni yakunlash
    res3 = engine.submit_quiz_answer(user_id, "fastapi", question_index=0, selected_option=1)
    assert res3["is_correct"] is True
    assert res3["is_course_completed"] is True
    assert res3["current_score"] == 20
    storage.close()
