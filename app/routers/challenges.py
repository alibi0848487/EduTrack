from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import Challenge, ChallengeParticipant, ChallengeStatus, User, CoinTransaction, TxType
from app.schemas.schemas import ChallengeCreate, ChallengeOut

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


def _to_out(challenge: Challenge) -> ChallengeOut:
    return ChallengeOut(
        id=challenge.id,
        title=challenge.title,
        description=challenge.description,
        skill_tag=challenge.skill_tag,
        coin_reward=challenge.coin_reward,
        max_participants=challenge.max_participants,
        deadline=challenge.deadline,
        status=challenge.status,
        participant_count=len(challenge.participants),
        created_at=challenge.created_at,
    )


@router.get("", response_model=List[ChallengeOut])
def list_challenges(status: str = "active", db: Session = Depends(get_db)):
    challenges = db.query(Challenge).filter(Challenge.status == status).all()
    return [_to_out(c) for c in challenges]


@router.get("/{challenge_id}", response_model=ChallengeOut)
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return _to_out(challenge)


@router.post("", response_model=ChallengeOut, status_code=201)
def create_challenge(
    body: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    challenge = Challenge(
        title=body.title,
        description=body.description,
        skill_tag=body.skill_tag,
        coin_reward=body.coin_reward,
        max_participants=body.max_participants,
        deadline=body.deadline,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return _to_out(challenge)


@router.post("/{challenge_id}/join", response_model=dict)
def join_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if challenge.status != ChallengeStatus.active:
        raise HTTPException(status_code=400, detail="Challenge is not active")
    if len(challenge.participants) >= challenge.max_participants:
        raise HTTPException(status_code=400, detail="Challenge is full")

    already = (
        db.query(ChallengeParticipant)
        .filter(
            ChallengeParticipant.challenge_id == challenge_id,
            ChallengeParticipant.user_id == current_user.id,
        )
        .first()
    )
    if already:
        raise HTTPException(status_code=409, detail="Already joined")

    db.add(ChallengeParticipant(challenge_id=challenge_id, user_id=current_user.id))
    db.commit()
    return {"detail": "Joined challenge", "challenge_id": challenge_id}


@router.post("/{challenge_id}/complete", response_model=dict)
def complete_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark challenge as completed and distribute coins to all participants."""
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if challenge.status != ChallengeStatus.active:
        raise HTTPException(status_code=400, detail="Challenge already completed or cancelled")

    challenge.status = ChallengeStatus.completed
    reward_per_user = challenge.coin_reward / max(len(challenge.participants), 1)

    for participant in challenge.participants:
        user = db.query(User).filter(User.id == participant.user_id).first()
        if user:
            user.skill_coins += reward_per_user
            db.add(CoinTransaction(
                user_id=user.id,
                amount=reward_per_user,
                tx_type=TxType.earn,
                reason="challenge_completed",
                ref_id=challenge.id,
            ))

    db.commit()
    return {"detail": "Challenge completed", "reward_per_user": reward_per_user}
