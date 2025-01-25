from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import Response
from dataclasses import dataclass
from pydantic import BaseModel
import datetime
import pytz
import os

from app import my_app
from graph.builder import ConversationLangGraph
from utils.chat_history import delete_chat_history


KR_TIMEZONE = pytz.timezone("Asia/Seoul")


chat_router = APIRouter()


@dataclass
class APIResponse:
    version: str
    template: dict


class Test_Message(BaseModel):
    user_id: str
    message: str | None = None


@chat_router.get("/")
async def index():
    """
    '상태 체크용 API'\n
    :return:
    """

    current_time = datetime.datetime.now(KR_TIMEZONE)
    return Response(
        f"samlltalk2rec server API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})"
    )


@chat_router.post("/callback")
async def handle_callback(request: Request):
    # try:
    data = await request.json()
    user_id = data.get("userRequest")["user"]["id"]  # 사용자의 고유 키
    message = data.get("userRequest")["utterance"]  # 사용자가 보낸 메시지

    # graph 결과 받아오기
    bot_response = my_app.graph.run(
        {
            "role": "user",
            "content": message,
        },
        user_id
    )

    # response 형태 수정
    response = APIResponse(
        version="2.0",
        template={"outputs": [{"simpleText": {"text": bot_response}}]},
    )

    return response


@chat_router.post("/callback/test")
async def handle_callback(test_message: Test_Message):
    # try:
    data = test_message.dict()
    user_id = str(data["user_id"])  # 사용자의 고유 키ß
    message = str(data["message"])  # 사용자가 보낸 메시지

    bot_response = my_app.graph.run(
        {
            "role": "user",
            "content": message,
        },
        user_id,
    )

    # response 형태 수정
    response = APIResponse(
        version="2.0",
        template={"outputs": [{"simpleText": {"text": bot_response}}]},
    )

    return response

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
