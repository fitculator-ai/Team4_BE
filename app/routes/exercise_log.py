from app.schemas import ExerciseLogCreate, ExerciseLogResponse, ExerciseLogUpdate, DeleteResponse, ExerciseLogView
from app.utils.db_operations import exercise_log_format, exercise_log_delete
from app.utils.utils import get_exercise_logs,get_user_info,exercise_intensity
from fastapi import APIRouter, Depends, HTTPException
from app.models import ExerciseLog
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from typing import List
from dateutil import tz

router = APIRouter()

# 운동 기록 추가 API (POST /api/exercise-logs)
@router.post("/", response_model=ExerciseLogResponse)
def create_exercise_logs(log: ExerciseLogCreate, db: Session = Depends(get_db)):
    user = get_user_info(db, log.user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_age = datetime.today().year - user.birth.year
    intensity_result = exercise_intensity(log.avg_bpm, user_age)
    new_log = exercise_log_format(db, log, intensity_result)
    return new_log


# 이번 주 운동 기록 확인 API (GET /api/exercise-logs/this-week)
@router.get("/this-week", response_model=List[ExerciseLogView])
def get_user_exercise_logs(user_id: int, db: Session = Depends(get_db)):
    request_time = datetime.now(tz.tzlocal())
    result = get_exercise_logs(user_id=user_id, db=db, date=request_time)
    return result


# 운동 기록 수정 API (PATCH /api/exercise-logs/{log_id})
@router.patch("/{log_id}")
def update_exercise_logs(log_id: int, log_update: ExerciseLogUpdate, db: Session = Depends(get_db)):
    exercise_data = db.query(ExerciseLog).filter(ExerciseLog.id == log_id).first()

    if not exercise_data:
        raise HTTPException(status_code=404, detail="운동 기록을 찾을 수 없습니다.")
    update_data = log_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(exercise_data, key, value)
    db.commit()
    db.refresh(exercise_data)
    
    return exercise_data


# 운동 기록 삭제 API (DELETE /api/exercise-logs/{log_id})
@router.delete("/{log_id}", response_model=DeleteResponse)
def delete_exercise_logs(log_id: int, db: Session = Depends(get_db)):
    exercise_log_delete(log_id, db)