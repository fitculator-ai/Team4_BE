from app.routes import exercise_log, points, exercise, user, mypage, check_server  # routes 폴더에서 라우터 파일 import
from app.database import Base, engine
from fastapi import FastAPI
import asyncio

app = FastAPI()

# 라우터 등록

app.include_router(user.router, prefix="/api/user", tags=["유저"])
app.include_router(mypage.router, prefix="/api/mypage", tags=["마이페이지"])
app.include_router(exercise_log.router, prefix="/api/exercise-logs", tags=["운동 기록"])
app.include_router(exercise.router, prefix="/api/exercise", tags=["운동 리스트"])
app.include_router(points.router, prefix="/api/points", tags=["포인트"])
app.include_router(check_server.router, prefix="/api/server-check", tags=["서버 체크"])


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(check_server.periodic_server_check())  # ✅ 2분마다 자동 실행

Base.metadata.create_all(bind=engine)



