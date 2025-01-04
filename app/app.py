from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class FastAPIApp:
    def __init__(self):
        # FastAPI 서버 생성
        self.app = FastAPI()

        # 다른 출처에서의 요청을 허용할지 정책 설정
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # 유저 id 및 이전 발화를 저장할 dictionary 생성
        self.user_converation = {}

        # 카카오톡 access, refresh 토큰 저장을 위한 dictionary 생성
        self.token_info = {
            "access_token": None,  # 최초 access_token은 authorizaion 토큰으로 발급
            "refresh_token": "YOUR_REFRESH_TOKEN",  # 최초에 수동으로 발급한 Refresh Token
            "expires_in": 3600,  # 만료 시간 (초 단위)
        }

    def include_router(self, router):
        self.app.include_router(router)


my_app = FastAPIApp()
