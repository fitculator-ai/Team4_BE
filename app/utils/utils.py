from sqlalchemy.orm import Session
from app.models import ExerciseLog, Exercise, User_detail
from app.schemas import ExerciseLogView, WeekExerciseLogView
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import jwt, JWTError

from decouple import config

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
        ExerciseLog.exercise_note,
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
        "exercise_note": log.exercise_note or None
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
    user = db.query(User_detail).filter(User_detail.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 유저를 찾을 수 없습니다.")
    return user

# 로그인 - 토큰 생성
def create_access_token(data: dict, expires_delta: timedelta = None):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=int(config("ACCESS_TOKEN_EXPIRE_MINUTES", default = 30))))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config("SECRET_KEY"), algorithm=config("ALGORITHM"))
    return encoded_jwt

# 토큰 검증
def get_sub_from_token(token: str):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 없습니다."
        )
    try:
        # verify_exp=False로 만료 여부를 확인하지 않음
        decoded_token = jwt.decode(token, config("SECRET_KEY"), algorithms=[config("ALGORITHM")], options={"verify_exp": False})
        return decoded_token.get("sub")  # sub 값 반환    
    except JWTError:
        # 토큰이 유효하지 않은 경우 (예: 위조된 토큰)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 유호하지 않습니다."
        )
    
# 최근 4주간 운동 기록 조회 
def get_last_4_weeks_exercise_logs(db: Session, user_id: int, date: datetime):
    all_weeks_logs = []

    for week_offset in range(4): # 총 4주
        target_date = date - timedelta(weeks=week_offset)
        monday, sunday = get_week_start_end(target_date)

        raw_data = (
            db.query(ExerciseLog, Exercise.exercise_name)
            .join(Exercise, ExerciseLog.exercise_id == Exercise.id)
            .filter(
                ExerciseLog.user_id == user_id,
                ExerciseLog.end_at.between(monday, sunday)
            )
            .all()
        )

        week_data = WeekExerciseLogView(
            week_start=monday.isoformat(),
            week_end=sunday.isoformat(),
            logs=[
                ExerciseLogView(
                    user_id=log.user_id,
                    exercise_name=exercise_name,
                    avg_bpm=log.avg_bpm,
                    max_bpm=log.max_bpm,
                    duration=log.duration,
                    end_at=log.end_at,
                    exercise_intensity=log.exercise_intensity,
                    earned_point=log.earned_point,
                    exercise_note=log.exercise_note if log.exercise_note else None
                )
                for log, exercise_name in raw_data
            ]
        )

        all_weeks_logs.append(week_data)

    return all_weeks_logs
