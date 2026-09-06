from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime

from app.database import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)

    comment_id = Column(Integer, unique=True, nullable=False)
    comment = Column(String, nullable=False)
    language = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    location = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)