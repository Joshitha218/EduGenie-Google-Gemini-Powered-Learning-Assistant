from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    UserID = Column(Integer, primary_key=True, index=True)
    UserName = Column(String, nullable=False)
    Email = Column(String, unique=True, index=True, nullable=False)
    PasswordHash = Column(String, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    # Relationships
    queries = relationship("UserQuery", back_populates="user", cascade="all, delete-orphan")
