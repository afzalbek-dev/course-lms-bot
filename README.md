# Course LMS Bot

Telegram orqali bosqichma-bosqich o'quv darslari (modullar), interaktiv test sinovlari (quizzes) va talabalar o'zlashtirish statistikasini yurituvchi ta'limiy LMS platformasi.

## Xususiyatlari
- **Bosqichma-bosqich O'rganish**: Talaba dars testini muvaffaqiyatli topshirmaguncha keyingi dars qulfdan ochilmaydi.
- **Interaktiv Quizlar**: Ko'p variantli test savollari, ballar hisobi va to'g'ri/noto'g'ri javoblarni tahlil qilish.
- **Progress Boshqaruvi**: Har bir foydalanuvchining joriy darsi, umumiy ballari va kursni bitirganlik holati SQLite bazasida saqlanadi.
- **CLI & Telegram Integratsiyasi**: Darslarni kiritish va talaba yutuqlarini tekshirish uchun qulay boshqaruv.

## Foydalanish (Python)
```python
from course_lms import LMSStorage, LMSEngine, QuizQuestion

storage = LMSStorage("courses.db")
engine = LMSEngine(storage)

# Darsni olish
lesson, prog = engine.get_current_lesson(user_id=123, course_id="python101")
print(f"Joriy dars: {lesson.title}")

# Testga javob berish
result = engine.submit_quiz_answer(user_id=123, course_id="python101", question_index=0, selected_option=1)
print("Natija:", result)
```

## CLI
```bash
course-lms seed
course-lms progress --user-id 999
course-lms answer --user-id 999 --q-idx 0 --option 1
```

## Testlar
```bash
pytest tests/ -v
```

## Litsenziya
MIT
