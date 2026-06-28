from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class AIResponse(Base):
    __tablename__ = "ai_responses"

    ResponseID = Column(Integer, primary_key=True, index=True)
    QueryID = Column(Integer, ForeignKey("user_queries.QueryID", ondelete="CASCADE"), nullable=False, unique=True)
    ResponseText = Column(Text, nullable=False)
    ModelUsed = Column(String, nullable=False)  # "Gemini", "LaMini-Flan-T5"
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    # Relationships
    query = relationship("UserQuery", back_populates="ai_response")
