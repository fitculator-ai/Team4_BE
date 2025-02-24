from app.models import GenderEnum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

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
    exercise_note: Optional[str] = ""  # None 

# 운동 기록 수정 모델
class ExerciseLogUpdate(BaseModel):
    avg_bpm: Optional[int] = None
    max_bpm: Optional[int] = None
    duration: Optional[int] = None
    end_at: Optional[datetime] = None
    earned_point: Optional[float] = None
    exercise_intensity: Optional[str] = None
    exercise_note: Optional[str] = None

# 운동 기록 조회 모델
class ExerciseLogView(BaseModel):
    user_id: int
    exercise_name: str
    avg_bpm: int
    max_bpm: int
    duration: int
    end_at: datetime
    exercise_intensity: str
    earned_point: float
    exercise_note: Optional[str] = None

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
    token: Optional[str] = None

# 유저 생성 응답값 검증 모델
class UserResponse(UserCreate):
    id: int
    name: str

    class Config:
        orm_mode = True

# 유저 상세정보 생성 검증 모델
class UserDetailCreate(BaseModel):
    user_id: int
    user_nickname: Optional[str] = None
    exercise_issue: Optional[str] = None
    exercise_goal: Optional[str] = None
    resting_bpm: Optional[int] = None
    height: Optional[float] = None
    birth: datetime
    device: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        orm_mode = True

# 유저 상세정보 조회 검증 모델
class UserDetailView(BaseModel):
    user_id: int
    user_nickname: str
    exercise_issue: str
    exercise_goal: str
    resting_bpm: int
    height: float
    birth: datetime
    device: str
    profile_image: str



# 유저 상세정보 수정 검증 모델
class UserDetailUpdate(BaseModel):
    user_nickname: Optional[str] = None
    exercise_issue: Optional[str] = None
    exercise_goal: Optional[str] = None
    resting_bpm: Optional[int] = None
    height: Optional[float] = None
    birth: datetime
    device: Optional[str] = None
    profile_image: Optional[str] = None

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

# 로그인 토큰
class UserLogin(BaseModel):
    token: str

class WeekExerciseLogView(BaseModel):
    week_start: str
    week_end: str
    logs: List[ExerciseLogView]