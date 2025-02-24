from app.models import ExerciseTypeEnum, Exercise
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List, Dict

router = APIRouter()

# 운동 리스트 조회 API
@router.get("/", response_model=Dict[str, List[str]], summary="유산소, 근력 운동들을 불러옴")
def get_exercise(db: Session = Depends(get_db)):

    cardio_ex = db.query(Exercise.exercise_name).filter(Exercise.exercise_type == ExerciseTypeEnum.Cardio).all()
    strength_ex = db.query(Exercise.exercise_name).filter(Exercise.exercise_type == ExerciseTypeEnum.Strength).all()

    cardio_list = [exercise.exercise_name for exercise in cardio_ex]
    strength_list = [exercise.exercise_name for exercise in strength_ex]

    exercise_list = {
        "유산소": cardio_list,
        "근력": strength_list
    }
    return exercise_list