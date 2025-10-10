from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from auth.jwt_handle import get_current_user
from models.user import User
from schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, NaturalLanguageInput
from services import schedule_service
from services.llm_schedule_parser import parse_natural_language_to_schedules
from typing import List
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/schedules", response_model=ScheduleResponse)
def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return schedule_service.create_schedule(db, schedule, current_user.id)

@router.post("/schedules/parse-and-create", response_model=List[ScheduleResponse])
def parse_and_create_schedules(
    input_data: NaturalLanguageInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        parsed_schedules = parse_natural_language_to_schedules(input_data.text)
    except TimeoutError:
        # 타임아웃 오류는 구체적으로 처리
        logger.warning(f"LLM 파싱 타임아웃: user={current_user.username}")
        raise HTTPException(status_code=408, detail="요청 처리 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")
    except json.JSONDecodeError as e:
        # JSON 파싱 오류는 로그에만 상세 기록
        logger.error(f"JSON 파싱 실패: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="일정 형식 변환 중 오류가 발생했습니다.")
    except Exception as e:
        # 기타 모든 오류는 일반 메시지로 처리, 서버 로그에만 상세 기록
        logger.error(f"LLM 파싱 실패: user={current_user.username}, error={str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="일정 파싱 중 오류가 발생했습니다. 다시 시도해주세요.")

    created_schedules = []
    for schedule in parsed_schedules:
        db_schedule = schedule_service.create_schedule(db, schedule, current_user.id)
        created_schedules.append(db_schedule)

    return created_schedules

@router.get("/schedules", response_model=List[ScheduleResponse])
def get_schedules(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return schedule_service.get_user_schedules(db, current_user.id, skip, limit)

@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    schedule = schedule_service.get_schedule(db, schedule_id, current_user.id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    schedule = schedule_service.update_schedule(db, schedule_id, current_user.id, schedule_update)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.delete("/schedules/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = schedule_service.delete_schedule(db, schedule_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted successfully"}
