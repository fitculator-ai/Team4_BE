# CRUD 함수 관리
from app.models import ExerciseLog, Exercise, ExerciseTypeEnum
from app.schemas import ExerciseLogCreate
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from app.utils.utils import get_week_start_end
from sqlalchemy import func
from dateutil import tz




# 운동기록 생성 함수
def exercise_log_format(db: Session, data: ExerciseLogCreate, intensity: str):
    try:
        new_exercise_log = ExerciseLog(
            user_id=data.user_id,
            exercise_id=data.exercise_id,
            avg_bpm=data.avg_bpm,
            max_bpm=data.max_bpm,
            duration=data.duration,
            end_at=data.end_at.replace(second=0, microsecond=0),
            exercise_intensity=intensity,
            earned_point=data.earned_point,
            exercise_note=data.exercise_note or ""
        )

        # 4. DB 저장
        db.add(new_exercise_log)
        db.commit()
        db.refresh(new_exercise_log)

        return new_exercise_log
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"운동 기록 중 오류 발생: {str(e)}")


# 운동기록 삭제 함수

def exercise_log_delete(log_id: int, db: Session):
    try:
        exercise_data = db.query(ExerciseLog).filter(ExerciseLog.id == log_id).first()
        db.delete(exercise_data)
        db.commit()
        return {"record_id": log_id, "message": "삭제가 완료되었습니다"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"운동 기록 삭제 중 오류 발생:{str(e)}")
    

def strength_count(db: Session, user_id: int, request_time: datetime):
    try:
        monday, sunday = get_week_start_end(request_time)  # 이번 주 월~일 계산

        strength_count = (
            db.query(func.count(ExerciseLog.id))
            .join(Exercise, Exercise.id == ExerciseLog.exercise_id)
            .filter(ExerciseLog.user_id == user_id)
            .filter(Exercise.exercise_type == ExerciseTypeEnum.Strength)  
            .filter(ExerciseLog.end_at.between(monday, sunday))
            .scalar() 
        )
        return strength_count  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")  
