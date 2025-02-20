from .routes import exercise_log, points, exercise, user  # routes 폴더에서 라우터 파일 import
from fastapi import FastAPI

app = FastAPI()

# 라우터 등록

app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(exercise_log.router, prefix="/api/exercise-logs", tags=["운동 기록"])
app.include_router(exercise.router, prefix="/api/exercise", tags=["운동 리스트"])
app.include_router(points.router, prefix="/api/points", tags=["포인트"])
