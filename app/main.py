from routes import exercise_log, points, exercise  # routes 폴더에서 라우터 파일 import
from fastapi import FastAPI

app = FastAPI()

# 라우터 등록
app.include_router(exercise_log.router, prefix="/api/exercise-logs", tags=["Exercise_Log"])
app.include_router(points.router, prefix="/api/points", tags=["Points"])
app.include_router(exercise.router, prefix="/api/exercise", tags=["Exercise-List"])