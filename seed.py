
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, Base, engine
import app.models.user  # noqa

Base.metadata.create_all(bind=engine)

from app.core.security import hash_password
from app.models.user import (
    Badge, Challenge, ChallengeStatus, Lesson, LessonCategory, LessonLevel,
    Skill, SkillType, User, CoinTransaction, TxType,
)

db = SessionLocal()

BADGES = [
    {"code": "mentor", "name": "Ментор", "description": "Провёл 5+ обменов", "icon": "🧑‍🏫"},
    {"code": "top_teacher", "name": "Учитель месяца", "description": "Лучший преподаватель", "icon": "🏆"},
    {"code": "top_student", "name": "Топ-ученик", "description": "Высокий рейтинг обучения", "icon": "🎓"},
    {"code": "newcomer", "name": "Новичок", "description": "Зарегистрировался на платформе", "icon": "🌱"},
]
for b in BADGES:
    if not db.query(Badge).filter(Badge.code == b["code"]).first():
        db.add(Badge(**b))
db.commit()

USERS = [
    {"name": "Иван Петров",    "email": "ivan@example.com",   "bio": "Разработчик, люблю Python и SQL",     "rating": 4.8, "skill_coins": 320},
    {"name": "Алия Сейтова",  "email": "aliya@example.com",  "bio": "UX/UI дизайнер из Алматы",            "rating": 4.6, "skill_coins": 215},
    {"name": "Марат Дюсенов", "email": "marat@example.com",  "bio": "Маркетолог, SMM-стратег",             "rating": 4.2, "skill_coins": 180},
    {"name": "Диана Ли",      "email": "diana@example.com",  "bio": "Преподаю английский и корейский",     "rating": 4.9, "skill_coins": 410},
    {"name": "Артём Козлов",  "email": "artem@example.com",  "bio": "Data Science, ML-энтузиаст",          "rating": 4.5, "skill_coins": 275},
]
SKILLS = {
    "ivan@example.com":  {"teach": ["Python", "SQL", "Django"], "learn": ["Figma", "UI Design"]},
    "aliya@example.com": {"teach": ["Figma", "UI Design", "Prototyping"], "learn": ["Python", "HTML/CSS"]},
    "marat@example.com": {"teach": ["SMM", "Marketing", "Copywriting"], "learn": ["SQL", "Excel"]},
    "diana@example.com": {"teach": ["English", "Korean"], "learn": ["Marketing", "Canva"]},
    "artem@example.com": {"teach": ["Machine Learning", "Pandas", "Python"], "learn": ["English", "Public Speaking"]},
}

for u_data in USERS:
    if db.query(User).filter(User.email == u_data["email"]).first():
        continue
    user = User(
        name=u_data["name"],
        email=u_data["email"],
        hashed_password=hash_password("password123"),
        bio=u_data["bio"],
        rating=u_data["rating"],
        skill_coins=u_data["skill_coins"],
    )
    db.add(user)
    db.flush()

    db.add(CoinTransaction(user_id=user.id, amount=user.skill_coins, tx_type=TxType.earn, reason="seed"))

    for skill_name in SKILLS[u_data["email"]]["teach"]:
        db.add(Skill(user_id=user.id, name=skill_name, skill_type=SkillType.teach, level="intermediate"))
    for skill_name in SKILLS[u_data["email"]]["learn"]:
        db.add(Skill(user_id=user.id, name=skill_name, skill_type=SkillType.learn))

db.commit()

ivan = db.query(User).filter(User.email == "ivan@example.com").first()
aliya = db.query(User).filter(User.email == "aliya@example.com").first()
artem = db.query(User).filter(User.email == "artem@example.com").first()
diana = db.query(User).filter(User.email == "diana@example.com").first()

LESSONS = [
    {"author": ivan,  "title": "SQL за 30 минут",           "skill_name": "SQL",            "category": LessonCategory.programming, "level": LessonLevel.beginner,     "coin_cost": 10, "views": 124, "description": "Основы SQL запросов"},
    {"author": ivan,  "title": "Django REST API с нуля",    "skill_name": "Django",         "category": LessonCategory.programming, "level": LessonLevel.intermediate,  "coin_cost": 20, "views": 89,  "description": "Создаём REST API"},
    {"author": aliya, "title": "Figma для начинающих",      "skill_name": "Figma",          "category": LessonCategory.design,      "level": LessonLevel.beginner,     "coin_cost": 15, "views": 201, "description": "Основы Figma"},
    {"author": aliya, "title": "UI Kit за 2 часа",          "skill_name": "UI Design",      "category": LessonCategory.design,      "level": LessonLevel.intermediate,  "coin_cost": 25, "views": 76,  "description": "Создаём UI Kit"},
    {"author": artem, "title": "Machine Learning basics",   "skill_name": "Machine Learning","category": LessonCategory.programming, "level": LessonLevel.intermediate,  "coin_cost": 30, "views": 143, "description": "Введение в ML"},
    {"author": diana, "title": "English for IT",            "skill_name": "English",        "category": LessonCategory.language,    "level": LessonLevel.beginner,     "coin_cost": 12, "views": 310, "is_live": True, "description": "Английский для разработчиков"},
]
for l in LESSONS:
    if not db.query(Lesson).filter(Lesson.title == l["title"]).first():
        db.add(Lesson(
            author_id=l["author"].id,
            title=l["title"],
            description=l.get("description"),
            skill_name=l["skill_name"],
            category=l["category"],
            level=l["level"],
            coin_cost=l["coin_cost"],
            views=l.get("views", 0),
            is_live=l.get("is_live", False),
        ))
db.commit()

CHALLENGES = [
    {"title": "Python марафон",        "description": "Напиши 5 скриптов за неделю",      "skill_tag": "Python",    "coin_reward": 100, "max_participants": 20},
    {"title": "UI/UX Battle",          "description": "Лучший редизайн мобильного экрана", "skill_tag": "Figma",     "coin_reward": 80,  "max_participants": 15},
    {"title": "English Speaking Club", "description": "30-минутная сессия каждый день",    "skill_tag": "English",   "coin_reward": 60,  "max_participants": 10},
]
for c in CHALLENGES:
    if not db.query(Challenge).filter(Challenge.title == c["title"]).first():
        db.add(Challenge(**c))
db.commit()

db.close()
print("✅ Seed completed! Demo users password: password123")
