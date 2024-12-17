import os

from fastapi import APIRouter, HTTPException

from pydantic import BaseModel
from starlette.requests import Request
import httpx
import requests
import time
import json



router = APIRouter()


ACCESS_TOKEN = os.getenv('KAKAO_ACCESS_TOKEN')  # 발급받은 Access Token
REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URL')
KAKAO_AUTHORIZATION_CODE = os.getenv('KAKAO_AUTHORIZATION_CODE')
TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"


TOKEN_INFO = {
    "access_token": None,
    "refresh_token": "YOUR_REFRESH_TOKEN",  # 최초에 수동으로 발급한 Refresh Token
    "expires_in": 0  # 만료 시간 (초 단위)
}

def get_access_token(authorization_code):
    """
    Authorization Code를 사용해 Access Token과 Refresh Token을 가져옵니다.
    """
    data = {
        "grant_type": "authorization_code",
        "client_id": ACCESS_TOKEN,
        "redirect_uri": REDIRECT_URI,
        "code": authorization_code,
    }

    response = requests.post(TOKEN_URL, data=data)
    print(response)
    if response.status_code == 200:
        print("access token 발급 완료")
        token_data = response.json()
        TOKEN_INFO["access_token"] = token_data.get("access_token")
        TOKEN_INFO["expires_in"] = token_data.get("expires_in", 0)

        # Refresh Token이 갱신되었을 경우 업데이트
        if "refresh_token" in token_data:
            TOKEN_INFO["refresh_token"] = token_data["refresh_token"]
        
        print("Access Token이 성공적으로 갱신되었습니다.")
    else:
        print("토큰 갱신 실패:", response.json())
        raise Exception("Failed to refresh Access Token")
    


def auto_refresh_token():
    """
    Access Token의 만료 시간을 확인하고 필요시 자동으로 갱신합니다.
    """
    if TOKEN_INFO["expires_in"] <= 0:
        print("Access Token 만료. 갱신 중...")
        get_access_token(KAKAO_AUTHORIZATION_CODE)

@router.post("/callback")
async def handle_callback(request: Request):
    try:
        auto_refresh_token()

        data = await request.json()
        print(data)
        sender_id = data.get("user_key")  # 사용자의 고유 키
        message = data.get("utterance")  # 사용자가 보낸 메시지

        # 사용자 메시지 처리
        # bot_response = await generate_response(message)
        return {
            "template_object":{
            "object_type":"text",
            "test":message+"asdklfjasdljflkdsjflkjaslkdfjlka"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        


        # 카카오에서 전달받은 데이터 확인


    # 사용자에게 답장 전송
    # await send_message_to_kakao(sender_id, bot_response)
    

    

async def generate_response(user_message):
    # 챗봇 로직 예제
    if user_message == "안녕":
        return "안녕하세요! 무엇을 도와드릴까요?123123123"
    return "죄송합니다, 이해하지 못했어요.1122131313"

# async def send_message_to_kakao(user_key, message):
#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             KAKAO_API_URL,
#             headers={
#                 "Authorization": f"Bearer {ACCESS_TOKEN}"
#             },
#             json={
#                 "template_object": {
#                     "object_type": "text",
#                     "text": message,
#                 }
#             }
#         )
#         if response.status_code != 200:
#             print(f"Failed to send message: {response.text}")
