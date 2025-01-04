from graph.builder import graph

from fastapi import APIRouter, HTTPException

from config import access_kakao
from app import my_app

from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response
import datetime, pytz


router = APIRouter()


@router.get("/")
async def index():
    """
    '상태 체크용 API'\n
    :return:
    """
    kr_timezone = pytz.timezone("Asia/Seoul")
    current_time = datetime.datetime.now(kr_timezone)
    return Response(
        f"samlltalk2rec server API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})"
    )


@router.post("/callback")
async def handle_callback(request: Request):
    try:
        access_kakao.auto_refresh_token(my_app)

        data = await request.json()
        print(data)
        user_id = data.get("user_key")  # 사용자의 고유 키
        message = data.get("userRequest")["utterance"]  # 사용자가 보낸 메시지

        if user_id not in my_app.user_conversations:
            # 할당된 chain이 없으면 생성 후 할당
            my_app.user_conversations[user_id] = ConversationalRetrievalChain(
                my_app.retriever
            )

        # 사전에 할당해 놓은 chain 불러와서 사용
        chain = my_app.user_conversations[user_id]

        # chain 결과 받아오기
        main_chain_result = chain.run(question)

        # 사용자 메시지 처리
        bot_response = graph.invoke({"messages": str(message)})["messages"][-1].content

        return {
            "version": "2.0",
            "template": {"outputs": [{"simpleText": {"text": bot_response}}]},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        # 카카오에서 전달받은 데이터 확인
