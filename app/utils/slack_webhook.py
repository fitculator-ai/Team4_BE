import httpx
from sqlalchemy.orm import Session
from app.config import DISCORD_WEBHOOK_URL
from app.database import SessionLocal
from app.models import Exercise

async def send_discord_webhook(content: str):
    """
    Discord 웹훅을 통해 메시지를 전송하는 함수
    """
    if not DISCORD_WEBHOOK_URL:
        raise ValueError("❌ DISCORD_WEBHOOK_URL이 설정되지 않았습니다!")

    message = {"content": content}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(DISCORD_WEBHOOK_URL, json=message)

        if response.status_code != 204:  # Discord는 204 응답이 성공
            raise Exception(f"Discord 웹훅 전송 실패 🚨: {response.text}")

    except httpx.HTTPError as e:
        print(f"💥 HTTP 요청 중 오류 발생: {e}")

async def post_exerciselog_webhook(exercise_id: int, user_id: int, user_nickname: str, duration: int):
    """
    운동 기록이 추가될 때 웹훅을 전송하는 함수
    """
    # ✅ 새롭게 DB 세션 열기
    db: Session = SessionLocal()

    try:
        # 운동명 조회 (이제 `exercise_id`를 직접 사용)
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

        if not exercise:
            raise ValueError(f"❌ 운동 ID {exercise_id}에 해당하는 운동을 찾을 수 없습니다.")

        # 웹훅 메시지 생성
        hook_log = (
            f"**운동 기록 추가됨**\n"
            f" 사용자 ID: {user_id}\n"
            f" 닉네임: {user_nickname}\n"
            f" 운동명: {exercise.exercise_name}\n"
            f" 운동시간: {duration}분\n"
        )

        # ✅ 비동기 웹훅 전송
        await send_discord_webhook(hook_log)

    finally:
        db.close()  # ✅ 세션 닫기