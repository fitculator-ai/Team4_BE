from app.utils.utils import get_week_start_end
from fastapi import APIRouter, Depends
from app.schemas import UserWeeklyPoints
from app.models import User, ExerciseLog
from sqlalchemy.orm import Session
from app.database import get_db
from datetime import datetime
from sqlalchemy import func
from dateutil import tz

router = APIRouter()

# 유저의 한 주간 포인트 
@router.get("/weekly", response_model = UserWeeklyPoints, summary="유저의 한 주간 포인트를 조회")
def get_user_weekly_points(user_id: int, db: Session = Depends(get_db)):
    request_time = datetime.now(tz.tzlocal()) # 요청이 들어온 시간
    monday, sunday = get_week_start_end(request_time)
    user_points = (
        db.query(func.sum(ExerciseLog.earned_point))
        .join(User, ExerciseLog.user_id == User.id)
        .filter(ExerciseLog.user_id == user_id,
                ExerciseLog.end_at.between(monday, sunday)
            )
        .scalar()
    )
    result = {"weekly_points" : round(user_points if user_points else 0, 2)}
    return result 