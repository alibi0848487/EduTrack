from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Skill, SkillType, CoinTransaction
from app.schemas.schemas import (
    CoinTransactionOut,
    ReviewOut,
    SkillCreate,
    SkillOut,
    UserOut,
    UserPublicOut,
    UserUpdateRequest,
)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_profile(
    body: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.name is not None:
        current_user.name = body.name
    if body.bio is not None:
        current_user.bio = body.bio
    if body.avatar_url is not None:
        current_user.avatar_url = body.avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserPublicOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ─── SKILLS ───────────────────────────────
@router.get("/me/skills", response_model=List[SkillOut])
def get_my_skills(current_user: User = Depends(get_current_user)):
    return current_user.skills


@router.post("/me/skills", response_model=SkillOut, status_code=201)
def add_skill(
    body: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.skill_type not in ("teach", "learn"):
        raise HTTPException(status_code=422, detail="skill_type must be 'teach' or 'learn'")

    existing = (
        db.query(Skill)
        .filter(
            Skill.user_id == current_user.id,
            Skill.name == body.name,
            Skill.skill_type == body.skill_type,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Skill already exists")

    skill = Skill(
        user_id=current_user.id,
        name=body.name,
        skill_type=body.skill_type,
        level=body.level or "beginner",
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.delete("/me/skills/{skill_id}", status_code=204)
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skill = db.query(Skill).filter(Skill.id == skill_id, Skill.user_id == current_user.id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()


# ─── COINS ────────────────────────────────
@router.get("/me/coins", response_model=List[CoinTransactionOut])
def get_coin_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 30,
    offset: int = 0,
):
    txs = (
        db.query(CoinTransaction)
        .filter(CoinTransaction.user_id == current_user.id)
        .order_by(CoinTransaction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return txs


# ─── REVIEWS ──────────────────────────────
@router.get("/{user_id}/reviews", response_model=List[ReviewOut])
def get_user_reviews(user_id: int, db: Session = Depends(get_db)):
    from app.models.user import Review

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.reviews_received
