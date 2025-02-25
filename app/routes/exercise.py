from app.models import ExerciseTypeEnum, Exercise
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List, Dict

router = APIRouter()

# 운동 리스트 조회 API
@router.get("/",  summary="유산소, 근력 운동들을 불러옴")
def get_exercise(db: Session = Depends(get_db)):

    cardio_exercise = db.query(Exercise.exercise_name, Exercise.id).filter(Exercise.exercise_type == ExerciseTypeEnum.Cardio).all()
    strength_exercise = db.query(Exercise.exercise_name, Exercise.id).filter(Exercise.exercise_type == ExerciseTypeEnum.Strength).all()

    cardio_list = [{"name" : exercise.exercise_name, "id" : exercise.id} for exercise in cardio_exercise]
    strength_list = [{"name" : exercise.exercise_name, "id" : exercise.id} for exercise in strength_exercise]

    exercise_list = {
        "유산소": cardio_list,
        "근력": strength_list
    }
    return exercise_list