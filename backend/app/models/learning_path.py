from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class LearningPath(Base):
    __tablename__ = "learning_paths"

    PathID = Column(Integer, primary_key=True, index=True)
    QueryID = Column(Integer, ForeignKey("user_queries.QueryID", ondelete="CASCADE"), nullable=False, unique=True)
    Topic = Column(String, nullable=False)
    Level = Column(String, nullable=False)  # e.g., "Beginner", "Intermediate", "Advanced", "All"
    Beginner = Column(Text, nullable=False)  # Beginner roadmap details (JSON/text)
    Intermediate = Column(Text, nullable=False)  # Intermediate roadmap details (JSON/text)
    Advanced = Column(Text, nullable=False)  # Advanced roadmap details (JSON/text)
    RecommendedTopics = Column(Text, nullable=True)  # Additional suggestions, certifications, projects, resources
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    # Relationships
    query = relationship("UserQuery", back_populates="learning_path")
