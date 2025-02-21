from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Exercise, ExerciseTypeEnum

def insert_exercise_data():
    db: Session = SessionLocal()

    # ✅ 유산소 운동 10개
    cardio_exercises = [
        "달리기", "사이클", "수영", "줄넘기", "등산",
        "조깅", "걷기", "로잉머신", "에어로빅", "스피닝"
    ]

    # ✅ 근력 운동 10개
    strength_exercises = [
        "스쿼트", "데드리프트", "벤치프레스", "풀업", "랫풀다운",
        "바벨 로우", "숄더 프레스", "런지", "케틀벨 스윙", "레그 프레스"
    ]

    # ✅ 기존 데이터 중복 방지
    existing_exercises = db.query(Exercise.exercise_name).all()
    existing_exercises = {exercise[0] for exercise in existing_exercises}

    # ✅ 유산소 운동 추가
    for exercise in cardio_exercises:
        if exercise not in existing_exercises:
            db.add(Exercise(exercise_name=exercise, exercise_type=ExerciseTypeEnum.Cardio))

    # ✅ 근력 운동 추가
    for exercise in strength_exercises:
        if exercise not in existing_exercises:
            db.add(Exercise(exercise_name=exercise, exercise_type=ExerciseTypeEnum.Strength))

    db.commit()
    db.close()
    print("✅ 운동 목록 데이터 삽입 완료!")

if __name__ == "__main__":
    insert_exercise_data()