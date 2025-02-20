from app.models import GenderEnum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 운동 기록 생성 pydantic 검증 모델
class ExerciseLogCreate(BaseModel):
    user_id: int
    exercise_id: int
    avg_bpm: int
    max_bpm: int
    duration: int
    end_at: datetime
    earned_point: float
    exercise_intensity: Optional[str] = None  # 추가 (FastAPI에서 오류 방지)
    exercise_detail: Optional[str] = ""  # None 

class ExerciseLogUpdate(BaseModel):
    avg_bpm: Optional[int] = None
    max_bpm: Optional[int] = None
    duration: Optional[int] = None
    end_at: Optional[datetime] = None
    earned_point: Optional[float] = None
    exercise_intensity: Optional[str] = None
    exercise_detail: Optional[str] = None

class ExerciseLogView(BaseModel):
    user_id: int
    exercise_name: str
    avg_bpm: int
    max_bpm: int
    duration: int
    end_at: datetime
    exercise_intensity: str
    earned_point: float
    exercise_detail: Optional[str] = None

# 운동 기록 응답값 검증 모델
class ExerciseLogResponse(ExerciseLogCreate):
    id: int

    model_config = {
        "orm_mode": True 
    }

# 유저 생성 검증 모델
class UserCreate(BaseModel):
    email: str
    name: str
    birth: Optional[datetime] = None
    gender: GenderEnum
    device: str

# 유저 생성 응답값 검증 모델
class UserResponse(UserCreate):
    id: int
    name: str

    class Config:
        orm_mode = True

# 유저의 주간 포인트 총합 검증 모델
class UserWeeklyPoints(BaseModel):
    weekly_points: float

# 운동기록 삭제 검증 모델(응답값)
class DeleteResponse(BaseModel):
    record_id: int
    message: str

# 근력운동 횟수
class StrengthCount(BaseModel):
    count: int


class UserLogin(BaseModel):
    token: str