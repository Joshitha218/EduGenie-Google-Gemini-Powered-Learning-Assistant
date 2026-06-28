from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Summary(Base):
    __tablename__ = "summaries"

    SummaryID = Column(Integer, primary_key=True, index=True)
    QueryID = Column(Integer, ForeignKey("user_queries.QueryID", ondelete="CASCADE"), nullable=False, unique=True)
    OriginalText = Column(Text, nullable=False)
    SummaryText = Column(Text, nullable=False)
    ModelUsed = Column(String, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    # Relationships
    query = relationship("UserQuery", back_populates="summary")
