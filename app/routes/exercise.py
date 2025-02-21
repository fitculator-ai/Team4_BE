from app.models import ExerciseTypeEnum, Exercise
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List

router = APIRouter()

# 운동 리스트 조회 API
@router.get("/", response_model=List[str])
def get_exercise(exercise_type: ExerciseTypeEnum = Query(None), db: Session = Depends(get_db)):
    query = db.query(Exercise.exercise_name)
    if exercise_type:
        query = query.filter(Exercise.exercise_type == exercise_type)

    exercises = query.all()
    return [exercise[0] for exercise in exercises]