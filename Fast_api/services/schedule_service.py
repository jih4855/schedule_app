from sqlalchemy.orm import Session
from Fast_api.models.schedule import Schedule
from Fast_api.schemas.schedule import ScheduleCreate, ScheduleUpdate
from typing import List, Optional

def create_schedule(db: Session, schedule: ScheduleCreate, user_id: int) -> Schedule:
    db_schedule = Schedule(
        title=schedule.title,
        description=schedule.description,
        scheduled_at=schedule.scheduled_at,
        user_id=user_id
    )
    db.add(db_schedule)
    return db_schedule

def get_user_schedules(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Schedule]:
    return db.query(Schedule).filter(Schedule.user_id == user_id).offset(skip).limit(limit).all()

def get_schedule(db: Session, schedule_id: int, user_id: int) -> Optional[Schedule]:
    return db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == user_id
    ).first()

def update_schedule(db: Session, schedule_id: int, user_id: int, schedule_update: ScheduleUpdate) -> Optional[Schedule]:
    db_schedule = get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return None

    update_data = schedule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)

    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_schedule(db: Session, schedule_id: int, user_id: int) -> bool:
    db_schedule = get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return False

    db.delete(db_schedule)
    db.commit()
    return True