from app.schemas import ExerciseLogCreate, ExerciseLogResponse, ExerciseNoteUpdate, DeleteResponse, ExerciseLogView
from app.utils.db_operations import exercise_log_format, exercise_log_delete, strength_count
from app.utils.utils import get_exercise_logs,get_user_info,exercise_intensity
from fastapi import APIRouter, Depends, HTTPException
from app.models import ExerciseLog
from sqlalchemy.orm import Session
from app.database import get_db
from datetime import datetime
from sqlalchemy import func
from typing import List
from dateutil import tz


router = APIRouter()

# 운동 기록 추가 API (POST /api/exercise-logs)
@router.post("/", response_model=ExerciseLogResponse, summary="유저의 운동 기록을 생성함")
def create_exercise_logs(log: ExerciseLogCreate, db: Session = Depends(get_db)):
    """사용자의 운동 기록 추가"""
    user = get_user_info(db, log.user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_age = datetime.today().year - user.birth.year
    intensity_result = exercise_intensity(log.avg_bpm, user_age)
    new_log = exercise_log_format(db, log, intensity_result)
    return new_log


# 이번 주 운동 기록 확인 API (GET /api/exercise-logs/this-week)
@router.get("/this-week", response_model=List[ExerciseLogView], summary="이번주 운동 기록들을 불러옴")
def get_user_exercise_logs(user_id: int, db: Session = Depends(get_db)):
    request_time = datetime.now(tz.tzlocal())
    result = get_exercise_logs(user_id=user_id, db=db, date=request_time)
    return result


# 운동 기록 수정 API (PATCH /api/exercise-logs/{log_id})
@router.patch("/{log_id}", summary="운동 기록 중 메모장 내용을 수정함")
def update_exercise_logs(log_id: int, log_update: ExerciseNoteUpdate, db: Session = Depends(get_db)):
    exercise_data = db.query(ExerciseLog).filter(ExerciseLog.id == log_id).first()

    if not exercise_data:
        raise HTTPException(status_code=404, detail="운동 기록을 찾을 수 없습니다.")
    
    exercise_data.exercise_note = log_update.exercise_note  

    db.commit()
    db.refresh(exercise_data)
    
    return exercise_data


# 운동 기록 삭제 API (DELETE /api/exercise-logs/{log_id})
@router.delete("/{log_id}", response_model=DeleteResponse, summary="운동 기록을 삭제함")
def delete_exercise_logs(log_id: int, db: Session = Depends(get_db)):
    message = exercise_log_delete(log_id, db)
    return message

@router.get("/strength/count", summary="이번 주 근력운동 횟수를 반환함.")
def count_strength(user_id: int, db: Session = Depends(get_db)):
    request_time = datetime.now(tz.tzlocal())  # 요청 시간
    count = strength_count(db, user_id, request_time)
    return {"count": count}

@router.get("/target-date", response_model=List[ExerciseLogView], summary="원하는 날짜를 입력하면 그 주(월~일)의 운동 기록을 불러옴")
def get_target_date_exercise_log(user_id: int, target_date: datetime, db: Session = Depends(get_db)):
    try:
        result = get_exercise_logs(user_id=user_id, db=db, date=target_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="정보를 찾을 수 없음")