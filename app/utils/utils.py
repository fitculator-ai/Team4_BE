from sqlalchemy.orm import Session
from app.models import ExerciseLog, Exercise, User
from fastapi import HTTPException
from datetime import datetime, timedelta

# 선택한 datetime의 월요일 일요일의 날짜를 반환하는 함수
def get_week_start_end(target_date: datetime):
    monday = target_date - timedelta(days=target_date.weekday())  # 해당 주의 월요일
    sunday = monday + timedelta(days=6)  # 해당 주의 일요일
    return monday.date(), sunday.date()

# 요청을 보낸 유저의 주간 운동 기록을 반환하는 함수
def get_exercise_logs(db: Session, user_id: int, date: datetime):
    monday, sunday = get_week_start_end(date)
    raw_data = (
    db.query(ExerciseLog, Exercise.exercise_name)
    .join(Exercise, ExerciseLog.exercise_id == Exercise.id)
    .filter(
        ExerciseLog.user_id == user_id,
        ExerciseLog.end_at.between(monday, sunday)
    )
    .group_by(
        ExerciseLog.id,
        ExerciseLog.user_id,
        ExerciseLog.exercise_id,
        ExerciseLog.avg_bpm,
        ExerciseLog.max_bpm,
        ExerciseLog.duration,
        ExerciseLog.end_at,
        ExerciseLog.exercise_intensity,
        ExerciseLog.earned_point,
        ExerciseLog.exercise_detail,
        Exercise.exercise_name
    )
    .order_by(ExerciseLog.end_at.desc())
    .all()
)
    return [
    {
        "id": log.id,
        "user_id": log.user_id,
        "exercise_name": exercise_name,
        "avg_bpm": log.avg_bpm,
        "max_bpm": log.max_bpm,
        "duration": log.duration,
        "end_at": log.end_at.isoformat(),
        "exercise_intensity": log.exercise_intensity,
        "earned_point": log.earned_point,
        "exercise_detail": log.exercise_detail or None
    }
    for log, exercise_name in raw_data 
]

# 운동 강도 측정 로직
def exercise_intensity(avg_bpm, age):
    hr_max = 220 - age
    avg_intensity = (avg_bpm / hr_max) * 100

    if avg_intensity < 40:
        return "매우 낮음"
    elif avg_intensity < 50:
        return "낮음"
    elif avg_intensity < 65:
        return "보통"
    elif avg_intensity < 80:
        return "높음"
    else:
        return "매우 높음"
    
# 유저의 유, 무를 판단하는 로직
def get_user_info(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 유저를 찾을 수 없습니다.")
    return user


