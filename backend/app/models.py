from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)