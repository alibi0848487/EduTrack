from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import Match, MatchStatus, Skill, SkillType, User, CoinTransaction, TxType
from app.schemas.schemas import MatchCreate, MatchOut, MatchStatusUpdate, MatchSuggestion, UserPublicOut

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("/suggestions", response_model=List[MatchSuggestion])
def get_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
):
    my_teach = {s.name.lower() for s in current_user.skills if s.skill_type == SkillType.teach}
    my_learn = {s.name.lower() for s in current_user.skills if s.skill_type == SkillType.learn}

    if not my_teach and not my_learn:
        return []

    candidates = (
        db.query(User)
        .filter(User.id != current_user.id, User.is_active == True)
        .all()
    )

    suggestions = []
    for candidate in candidates:
        c_teach = {s.name.lower(): s.name for s in candidate.skills if s.skill_type == SkillType.teach}
        c_learn = {s.name.lower(): s.name for s in candidate.skills if s.skill_type == SkillType.learn}

        learnable = my_learn & set(c_teach.keys())
        teachable = my_teach & set(c_learn.keys())

        if not learnable and not teachable:
            continue

        total = len(my_teach | my_learn | set(c_teach.keys()) | set(c_learn.keys())) or 1
        overlap_score = (len(learnable) + len(teachable)) / total
        rating_factor = 1 + (candidate.rating / 10)  # boost by rating
        score = min(overlap_score * rating_factor, 1.0)

        teach_skill = next(iter(c_teach.get(k, k) for k in learnable), "") if learnable else (next(iter(c_teach.values()), ""))
        learn_skill = next(iter(c_learn.get(k, k) for k in teachable), "") if teachable else (next(iter(c_learn.values()), ""))

        suggestions.append(MatchSuggestion(
            user=UserPublicOut.model_validate(candidate),
            teach_skill=teach_skill,
            learn_skill=learn_skill,
            score=round(score, 3),
        ))

    suggestions.sort(key=lambda s: s.score, reverse=True)
    return suggestions[:limit]


@router.post("", response_model=MatchOut, status_code=201)
def create_match(
    body: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.target_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot match with yourself")

    target = db.query(User).filter(User.id == body.target_id, User.is_active == True).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    # Avoid duplicate pending match
    existing = (
        db.query(Match)
        .filter(
            Match.requester_id == current_user.id,
            Match.target_id == body.target_id,
            Match.status == MatchStatus.pending,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Match request already pending")

    match = Match(
        requester_id=current_user.id,
        target_id=body.target_id,
        teach_skill=body.teach_skill,
        learn_skill=body.learn_skill,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.get("", response_model=List[MatchOut])
def list_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    matches = (
        db.query(Match)
        .filter(
            (Match.requester_id == current_user.id) | (Match.target_id == current_user.id)
        )
        .order_by(Match.created_at.desc())
        .all()
    )
    return matches


@router.get("/{match_id}", response_model=MatchOut)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.requester_id != current_user.id and match.target_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return match


@router.patch("/{match_id}/status", response_model=MatchOut)
def update_match_status(
    match_id: int,
    body: MatchStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    allowed_statuses = {"accepted", "declined", "completed"}
    if body.status not in allowed_statuses:
        raise HTTPException(status_code=422, detail=f"Status must be one of {allowed_statuses}")

    if body.status in ("accepted", "declined") and match.target_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the match target can accept or decline")

    if body.status == "completed" and match.status != MatchStatus.accepted:
        raise HTTPException(status_code=400, detail="Match must be accepted before completing")

    match.status = body.status

    if body.status == "completed":
        reward = 15.0
        for uid in (match.requester_id, match.target_id):
            user = db.query(User).filter(User.id == uid).first()
            if user:
                user.skill_coins += reward
                db.add(CoinTransaction(
                    user_id=uid,
                    amount=reward,
                    tx_type=TxType.earn,
                    reason="match_completed",
                    ref_id=match.id,
                ))

    db.commit()
    db.refresh(match)
    return match
