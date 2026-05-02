from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank")
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    bio: Optional[str]
    avatar_url: Optional[str]
    rating: float
    skill_coins: float
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


class UserPublicOut(BaseModel):
    id: int
    name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    rating: float
    skill_coins: float
    skills: List[SkillOut] = []
    badges: List[BadgeOut] = []

    model_config = {"from_attributes": True}


class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    skill_type: str  # "teach" | "learn"
    level: Optional[str] = "beginner"


class SkillOut(BaseModel):
    id: int
    name: str
    skill_type: str
    level: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class LessonCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    skill_name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = "other"
    level: Optional[str] = "beginner"
    coin_cost: float = Field(10.0, ge=0, le=500)
    video_url: Optional[str] = None
    is_live: bool = False


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    skill_name: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    coin_cost: Optional[float] = Field(None, ge=0, le=500)
    video_url: Optional[str] = None
    is_live: Optional[bool] = None


class LessonOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    skill_name: str
    category: str
    level: str
    coin_cost: float
    video_url: Optional[str]
    is_live: bool
    views: int
    created_at: datetime
    author: UserOut

    model_config = {"from_attributes": True}


class MatchCreate(BaseModel):
    target_id: int
    teach_skill: str = Field(..., min_length=1, max_length=100)
    learn_skill: str = Field(..., min_length=1, max_length=100)


class MatchStatusUpdate(BaseModel):
    status: str  # "accepted" | "declined" | "completed"


class MatchOut(BaseModel):
    id: int
    requester: UserOut
    target: UserOut
    teach_skill: str
    learn_skill: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MatchSuggestion(BaseModel):
    user: UserPublicOut
    teach_skill: str   # they teach what you want to learn
    learn_skill: str   # they want to learn what you teach
    score: float       # match quality 0–1


class ChallengeCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    skill_tag: Optional[str] = None
    coin_reward: float = Field(50.0, ge=0, le=1000)
    max_participants: int = Field(10, ge=2, le=100)
    deadline: Optional[datetime] = None


class ChallengeOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    skill_tag: Optional[str]
    coin_reward: float
    max_participants: int
    deadline: Optional[datetime]
    status: str
    participant_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    reviewed_id: int
    match_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewOut(BaseModel):
    id: int
    reviewer: UserOut
    rating: int
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class BadgeOut(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    earned_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CoinTransactionOut(BaseModel):
    id: int
    amount: float
    tx_type: str
    reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    user: UserOut
    value: float
    label: str
