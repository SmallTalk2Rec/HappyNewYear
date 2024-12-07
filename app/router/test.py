import os

from fastapi import APIRouter

from pydantic import BaseModel
from starlette.requests import Request
import httpx


router = APIRouter()


KAKAO_API_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"  # 카카오 API 엔드포인트
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')  # 발급받은 Access Token


@router.post("/callback")
async def handle_callback(request: Request):
    data = await request.json()

    # 카카오에서 전달받은 데이터 확인
    sender_id = data.get("user_key")  # 사용자의 고유 키
    message = data.get("message")  # 사용자가 보낸 메시지

    # 사용자 메시지 처리
    bot_response = await generate_response(message)

    # 사용자에게 답장 전송
    await send_message_to_kakao(sender_id, bot_response)

    return {"status": "received"}

async def generate_response(user_message):
    # 챗봇 로직 예제
    if user_message == "안녕":
        return "안녕하세요! 무엇을 도와드릴까요?"
    return "죄송합니다, 이해하지 못했어요."

async def send_message_to_kakao(user_key, message):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            KAKAO_API_URL,
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}"
            },
            json={
                "template_object": {
                    "object_type": "text",
                    "text": message,
                }
            }
        )
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")
