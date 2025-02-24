from app.utils.utils import get_week_start_end
from app.models import User, ExerciseLog
from fastapi import APIRouter, Depends
from app.schemas import UserPoints
from sqlalchemy.orm import Session
from app.database import get_db
from datetime import datetime
from sqlalchemy import func
from dateutil import tz

router = APIRouter()

# 유저의 한 주간 포인트 
@router.get("/{target_date}", response_model = UserPoints, summary="유저의 한 주간 포인트를 조회")
def get_user_weekly_points(user_id: int, target_date: datetime, db: Session = Depends(get_db)):
    monday, sunday = get_week_start_end(target_date)
    user_points = (
        db.query(func.sum(ExerciseLog.earned_point))
        .join(User, ExerciseLog.user_id == User.id)
        .filter(ExerciseLog.user_id == user_id,
                ExerciseLog.end_at.between(monday, sunday)
            )
        .scalar()
    )
    result = {
        "range" : f"{monday} ~ {sunday}",
        "points" : round(user_points if user_points else 0, 2)
        }
    return result 