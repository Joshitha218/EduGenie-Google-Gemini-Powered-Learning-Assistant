from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    QuizID = Column(Integer, primary_key=True, index=True)
    QueryID = Column(Integer, ForeignKey("user_queries.QueryID", ondelete="CASCADE"), nullable=False)
    QuestionText = Column(Text, nullable=False)
    OptionA = Column(String, nullable=False)
    OptionB = Column(String, nullable=False)
    OptionC = Column(String, nullable=False)
    OptionD = Column(String, nullable=False)
    CorrectOption = Column(String(1), nullable=False)  # "A", "B", "C", or "D"
    Explanation = Column(Text, nullable=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    # Relationships
    query = relationship("UserQuery", back_populates="quizzes")
