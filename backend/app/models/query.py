from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class UserQuery(Base):
    __tablename__ = "user_queries"

    QueryID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.UserID", ondelete="CASCADE"), nullable=False)
    QueryType = Column(String, nullable=False)  # "qa", "explain", "quiz", "summarize", "learn"
    QueryText = Column(String, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="queries")
    ai_response = relationship("AIResponse", back_populates="query", uselist=False, cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="query", cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="query", uselist=False, cascade="all, delete-orphan")
    learning_path = relationship("LearningPath", back_populates="query", uselist=False, cascade="all, delete-orphan")
