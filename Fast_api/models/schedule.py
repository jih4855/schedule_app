from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from Fast_api.db.base_class import Base
from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo('Asia/Seoul')

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(KST))
    updated_at = Column(DateTime, default=lambda: datetime.now(KST), onupdate=lambda: datetime.now(KST))
