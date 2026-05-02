from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user, get_optional_user
from app.models.user import Lesson, User, CoinTransaction, TxType
from app.schemas.schemas import LessonCreate, LessonOut, LessonUpdate

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


def _lesson_or_404(lesson_id: int, db: Session) -> Lesson:
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.get("", response_model=List[LessonOut])
def list_lessons(
    q: Optional[str] = Query(None, description="Search by title or skill"),
    category: Optional[str] = None,
    level: Optional[str] = None,
    is_live: Optional[bool] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Lesson)
    if q:
        like = f"%{q}%"
        query = query.filter(
            Lesson.title.ilike(like) | Lesson.skill_name.ilike(like) | Lesson.description.ilike(like)
        )
    if category:
        query = query.filter(Lesson.category == category)
    if level:
        query = query.filter(Lesson.level == level)
    if is_live is not None:
        query = query.filter(Lesson.is_live == is_live)

    return query.order_by(Lesson.views.desc(), Lesson.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/popular", response_model=List[LessonOut])
def popular_lessons(limit: int = 6, db: Session = Depends(get_db)):
    return db.query(Lesson).order_by(Lesson.views.desc()).limit(limit).all()


@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = _lesson_or_404(lesson_id, db)
    lesson.views += 1
    db.commit()
    db.refresh(lesson)
    return lesson


@router.post("", response_model=LessonOut, status_code=201)
def create_lesson(
    body: LessonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = Lesson(
        author_id=current_user.id,
        title=body.title,
        description=body.description,
        skill_name=body.skill_name,
        category=body.category or "other",
        level=body.level or "beginner",
        coin_cost=body.coin_cost,
        video_url=body.video_url,
        is_live=body.is_live,
    )
    db.add(lesson)
    db.flush()

    # Reward author
    reward = settings.LESSON_CREATE_REWARD
    current_user.skill_coins += reward
    db.add(CoinTransaction(
        user_id=current_user.id,
        amount=reward,
        tx_type=TxType.earn,
        reason="lesson_created",
        ref_id=lesson.id,
    ))
    db.commit()
    db.refresh(lesson)
    return lesson


@router.put("/{lesson_id}", response_model=LessonOut)
def update_lesson(
    lesson_id: int,
    body: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = _lesson_or_404(lesson_id, db)
    if lesson.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your lesson")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(lesson, field, value)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/{lesson_id}", status_code=204)
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lesson = _lesson_or_404(lesson_id, db)
    if lesson.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your lesson")
    db.delete(lesson)
    db.commit()


@router.post("/{lesson_id}/enroll", response_model=dict)
def enroll_in_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Buy a lesson with SkillCoins."""
    lesson = _lesson_or_404(lesson_id, db)
    if lesson.author_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot enroll in your own lesson")
    if current_user.skill_coins < lesson.coin_cost:
        raise HTTPException(status_code=402, detail="Insufficient SkillCoins")

    # Deduct from student
    current_user.skill_coins -= lesson.coin_cost
    db.add(CoinTransaction(
        user_id=current_user.id,
        amount=-lesson.coin_cost,
        tx_type=TxType.spend,
        reason="lesson_enrolled",
        ref_id=lesson.id,
    ))

    # Credit author
    author = db.query(User).filter(User.id == lesson.author_id).first()
    if author:
        author.skill_coins += lesson.coin_cost
        db.add(CoinTransaction(
            user_id=author.id,
            amount=lesson.coin_cost,
            tx_type=TxType.earn,
            reason="lesson_taught",
            ref_id=lesson.id,
        ))

    db.commit()
    return {"detail": "Enrolled successfully", "coins_spent": lesson.coin_cost}
