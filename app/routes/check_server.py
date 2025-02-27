from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import DISCORD_WEBHOOK_URL
import httpx, asyncio

router = APIRouter()


@router.get("/", summary="서버 및 API 상태 확인")
async def server_check(db: Session = Depends(get_db)):
    status_report = []

    # ✅ 1. DB 상태 확인
    try:
        db.execute(text("SELECT 1"))  
        status_report["서버 상태"] = "✅ 연결 정상"
    except Exception as e:
        status_report["서버 상태"] = f"🚨 연결 실패 - {str(e)}"

    return status_report

async def send_health_webhook(status_report: str):
    """
    서버 상태를 Discord Webhook으로 전송하는 함수 (단일 문자열)
    """
    if not DISCORD_WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK_URL이 설정되지 않았습니다!")
        return
    message_data = {"content": status_report.strip()}  # ✅ 문자열로 바로 전송
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(DISCORD_WEBHOOK_URL, json=message_data)

        if response.status_code != 204:
            print(f"🚨 웹훅 전송 실패: {response.text}")

    except httpx.HTTPError as e:
        print(f"💥 HTTP 요청 중 오류 발생: {e}")

async def periodic_server_check():
    """
    2분마다 서버 상태를 확인하고 Webhook으로 전송
    """
    while True:
        db: Session = next(get_db())
        try:
            db.execute(text("SELECT 1"))
            db_status = "✅ 서버 연결 정상"
        except Exception as e:
            db_status = f"🚨 서버 연결 실패 - {str(e)}"
        finally:
            db.close()

        await send_health_webhook(db_status)

        await asyncio.sleep(180)