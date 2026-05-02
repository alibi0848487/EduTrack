from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import Review, User
from app.schemas.schemas import LeaderboardEntry, ReviewCreate, ReviewOut, UserOut

leaderboard_router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@leaderboard_router.get("/coins", response_model=List[LeaderboardEntry])
def leaderboard_coins(limit: int = 10, db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .filter(User.is_active == True)
        .order_by(User.skill_coins.desc())
        .limit(limit)
        .all()
    )
    return [
        LeaderboardEntry(rank=i + 1, user=UserOut.model_validate(u), value=u.skill_coins, label="SkillCoins")
        for i, u in enumerate(users)
    ]


@leaderboard_router.get("/rating", response_model=List[LeaderboardEntry])
def leaderboard_rating(limit: int = 10, db: Session = Depends(get_db)):
    users = (
        db.query(User)
        .filter(User.is_active == True)
        .order_by(User.rating.desc())
        .limit(limit)
        .all()
    )
    return [
        LeaderboardEntry(rank=i + 1, user=UserOut.model_validate(u), value=u.rating, label="Rating")
        for i, u in enumerate(users)
    ]


reviews_router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@reviews_router.post("", response_model=ReviewOut, status_code=201)
def create_review(
    body: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.reviewed_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot review yourself")

    target = db.query(User).filter(User.id == body.reviewed_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    review = Review(
        reviewer_id=current_user.id,
        reviewed_id=body.reviewed_id,
        match_id=body.match_id,
        rating=body.rating,
        comment=body.comment,
    )
    db.add(review)
    db.flush()

    all_reviews = db.query(Review).filter(Review.reviewed_id == body.reviewed_id).all()
    if all_reviews:
        target.rating = sum(r.rating for r in all_reviews) / len(all_reviews)

    db.commit()
    db.refresh(review)
    return review
