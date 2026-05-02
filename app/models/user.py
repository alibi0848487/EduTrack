import enum
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, Float,
    ForeignKey, Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(512), nullable=True)
    rating = Column(Float, default=0.0)
    skill_coins = Column(Float, default=100.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="author", cascade="all, delete-orphan")
    coin_transactions = relationship("CoinTransaction", back_populates="user", cascade="all, delete-orphan")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")
    reviews_given = relationship("Review", foreign_keys="Review.reviewer_id", back_populates="reviewer")
    reviews_received = relationship("Review", foreign_keys="Review.reviewed_id", back_populates="reviewed")


class SkillType(str, enum.Enum):
    teach = "teach"
    learn = "learn"


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("user_id", "name", "skill_type"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    skill_type = Column(Enum(SkillType), nullable=False)
    level = Column(String(20), default="beginner") 
    created_at = Column(DateTime(timezone=True), default=utcnow)

    user = relationship("User", back_populates="skills")


class LessonLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class LessonCategory(str, enum.Enum):
    programming = "programming"
    design = "design"
    marketing = "marketing"
    language = "language"
    other = "other"


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    skill_name = Column(String(100), nullable=False)
    category = Column(Enum(LessonCategory), default=LessonCategory.other)
    level = Column(Enum(LessonLevel), default=LessonLevel.beginner)
    coin_cost = Column(Float, default=10.0)
    video_url = Column(String(512), nullable=True)
    is_live = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    author = relationship("User", back_populates="lessons")



class MatchStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    completed = "completed"


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    teach_skill = Column(String(100), nullable=False)  
    learn_skill = Column(String(100), nullable=False)   
    status = Column(Enum(MatchStatus), default=MatchStatus.pending)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    requester = relationship("User", foreign_keys=[requester_id])
    target = relationship("User", foreign_keys=[target_id])


class ChallengeStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    skill_tag = Column(String(100), nullable=True)
    coin_reward = Column(Float, default=50.0)
    max_participants = Column(Integer, default=10)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(ChallengeStatus), default=ChallengeStatus.active)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    participants = relationship("ChallengeParticipant", back_populates="challenge", cascade="all, delete-orphan")


class ChallengeParticipant(Base):
    __tablename__ = "challenge_participants"
    __table_args__ = (UniqueConstraint("challenge_id", "user_id"),)

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime(timezone=True), default=utcnow)

    challenge = relationship("Challenge", back_populates="participants")
    user = relationship("User")



class TxType(str, enum.Enum):
    earn = "earn"
    spend = "spend"
    transfer = "transfer"


class CoinTransaction(Base):
    __tablename__ = "coin_transactions"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)         
    tx_type = Column(Enum(TxType), nullable=False)
    reason = Column(String(255), nullable=True)     
    ref_id = Column(Integer, nullable=True)        
    created_at = Column(DateTime(timezone=True), default=utcnow)

    user = relationship("User", back_populates="coin_transactions")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("reviewer_id", "reviewed_id", "match_id"),)

    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reviewed_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="SET NULL"), nullable=True)
    rating = Column(Integer, nullable=False)   # 1–5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    reviewed = relationship("User", foreign_keys=[reviewed_id], back_populates="reviews_received")


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)   
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(10), nullable=True)


class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    earned_at = Column(DateTime(timezone=True), default=utcnow)

    user = relationship("User", back_populates="badges")
    badge = relationship("Badge")
