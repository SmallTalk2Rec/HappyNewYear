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
    print(data)
    user_id = data.get("userRequest")["user"]["id"]  # 사용자의 고유 키
    message = data.get("userRequest")["utterance"]  # 사용자가 보낸 메시지
    message = [{"role": "user", "content": message}]
    if user_id not in my_app.user_conversations:
        my_app.user_conversations[user_id] = {}
        # 할당된 chain이 없으면 생성 후 할당
        my_app.user_conversations[user_id]["langgraph"] = ConversationLangGraph()
        # my_app.user_conversations[user_id]["message"] = [
        #     {
        #         "role": "ai",
        #         "content": "안녕하세요 영화 추천 챗봇입니다. 무엇을 도와 드릴까요?",
        #     }
        # ]
    # 사전에 할당해 놓은 chain 불러와서 사용
    print("graph 객체 할당 완료")

    my_app.user_conversations[user_id]["message"] = message

    # graph 결과 받아오기
    bot_response = my_app.user_conversations[user_id]["langgraph"].run(
        my_app.user_conversations[user_id]["message"], user_id
    )
    print("graph 객체 할당 완료")

    # response 형태 수정
    response = APIResponse(
        version="2.0",
        template={"outputs": [{"simpleText": {"text": bot_response}}]},
    )

    # 이미 스케줄러에 등록되어 있으면 삭제 후에 작업 등록
    try:
        job = my_app.scheduler.get_job(user_id)
        job.remove()
    except Exception:
        pass

    my_app.scheduler.add_job(
        delete_chat_history,
        "date",
        run_date=datetime.datetime.now(KR_TIMEZONE) + datetime.timedelta(hours=1),
        id=user_id,
        args=[user_id, my_app.user_conversations],
    )

    return response


@chat_router.post("/callback/test")
async def handle_callback(test_message: Test_Message):
    # try:
    data = test_message.dict()
    print(data)
    user_id = str(data["user_id"])  # 사용자의 고유 키ß
    message = str(data["message"])  # 사용자가 보낸 메시지
    if user_id not in my_app.user_conversations:
        my_app.user_conversations[user_id] = {}
        # 할당된 chain이 없으면 생성 후 할당
        my_app.user_conversations[user_id]["langgraph"] = ConversationLangGraph()
        # my_app.user_conversations[user_id]["message"] = [
        #     {
        #         "role": "ai",
        #         "content": "안녕하세요 영화 추천 챗봇입니다. 무엇을 도와 드릴까요?",
        #     }
        # ]
    # 사전에 할당해 놓은 chain 불러와서 사용
    print("graph 객체 할당 완료")

    my_app.user_conversations[user_id]["message"] = message

    # graph 결과 받아오기
    bot_response = my_app.user_conversations[user_id]["langgraph"].run(
        my_app.user_conversations[user_id]["message"], user_id
    )
    print("graph 객체 할당 완료")

    # response 형태 수정
    response = APIResponse(
        version="2.0",
        template={"outputs": [{"simpleText": {"text": bot_response}}]},
    )

    # 이미 스케줄러에 등록되어 있으면 삭제 후에 작업 등록
    try:
        job = my_app.scheduler.get_job(user_id)
        job.remove()
    except Exception:
        pass

    my_app.scheduler.add_job(
        delete_chat_history,
        "date",
        run_date=datetime.datetime.now(KR_TIMEZONE) + datetime.timedelta(hours=1),
        id=user_id,
        args=[user_id, my_app.user_conversations],
    )

    return response

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
