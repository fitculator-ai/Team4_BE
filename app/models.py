from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float, Double
from sqlalchemy.orm import relationship
from database import Base
import enum

# 운동 타입 ENUM
class ExerciseTypeEnum(enum.Enum):
    Cardio = "유산소"
    Strength = "근력"

# 유저 테이블(로그인 시)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# 유저 상세 테이블
class User_detail(Base):
    __tablename__ = "user_details"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_issue = Column(String, nullable=True)
    exercise_goal = Column(String, nullable=True)
    resting_bpm = Column(Integer, nullable=True)
    height = Column(Float, nullable=True)
    birth = Column(DateTime, nullable=False)
    device = Column(String, nullable=True)
    profile_image = Column(String, nullable=True)

# 운동 목록 테이블
class Exercise(Base):
    __tablename__ = "exercise_list"

    id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String, nullable=False)
    exercise_type = Column(Enum(ExerciseTypeEnum), nullable=False)

# 운동 기록 테이블
# 운동 기록 테이블
class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id = Column(Integer, primary_key=True, index=True)    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)   # 유저 아이디 FK
    exercise_id = Column(Integer, ForeignKey("exercise_list.id"), nullable=False)  # 운동 아이디 FK
    avg_bpm = Column(Integer, nullable=True)  
    duration = Column(Integer, nullable=True)  
    end_at = Column(DateTime, nullable=True)  
    earned_point = Column(Float, nullable=False)
    exercise_intensity = Column(String, nullable=True)  
    exercise_note = Column(String, nullable=True)
    max_bpm = Column(Integer, nullable=True)  


