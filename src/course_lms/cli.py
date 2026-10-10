import argparse
import sys
import json
from .storage import LMSStorage
from .engine import LMSEngine
from .models import QuizQuestion


def main():
    parser = argparse.ArgumentParser(description="Course LMS Bot - Kurslar va testlar boshqaruvi")
    parser.add_argument("--db", default="/tmp/lms.db", help="SQLite ma'lumotlar bazasi fayli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_p = subparsers.add_parser("seed", help="Demo kurs va darslarni yuklash")
    progress_p = subparsers.add_parser("progress", help="Talaba holatini ko'rish")
    progress_p.add_argument("--user-id", type=int, required=True, help="Telegram User ID")
    progress_p.add_argument("--course", default="python101", help="Kurs ID")

    answer_p = subparsers.add_parser("answer", help="Test savoliga javob berish")
    answer_p.add_argument("--user-id", type=int, required=True)
    answer_p.add_argument("--course", default="python101")
    answer_p.add_argument("--q-idx", type=int, default=0)
    answer_p.add_argument("--option", type=int, required=True)

    args = parser.parse_args()
    storage = LMSStorage(args.db)
    engine = LMSEngine(storage)

    if args.command == "seed":
        storage.create_course("python101", "Python Asoslari", "Dasturlashga kirish kursi")
        q1 = QuizQuestion("Pythonda o'zgaruvchi qanday e'lon qilinadi?", ["let x = 5", "x = 5", "int x = 5"], 1)
        storage.add_lesson("python101", 1, "1-Dars: Kirish va O'zgaruvchilar", "Python dinamik tipli tildir...", [q1])

        q2 = QuizQuestion("Pythonda ro'yxat (list) belgisi nima?", ["{}", "()", "[]"], 2)
        storage.add_lesson("python101", 2, "2-Dars: Ro'yxatlar va Lug'atlar", "List va Dict tushunchalari...", [q2])
        print("✅ Demo kurs va 2 ta dars muvaffaqiyatli yuklandi!")
    elif args.command == "progress":
        prog = storage.get_progress(args.user_id, args.course)
        print(f"Talaba #{prog.user_id} | Kurs: {prog.course_id}")
        print(f"Joriy dars : #{prog.current_lesson_index}")
        print(f"Jami ball  : {prog.total_quiz_score}")
        print(f"Tugatilgan : {'Ha' if prog.is_completed else 'Yo\'q'}")
    elif args.command == "answer":
        res = engine.submit_quiz_answer(args.user_id, args.course, args.q_idx, args.option)
        print("Natija:", json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
