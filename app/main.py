import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import check_server,test
from starlette.responses import Response
import datetime, pytz




class FastAPIApp:
    def __init__(self):
        super().__init__()
        # FastAPI 서버 생성
        self.app = FastAPI()

        # 다른 출처에서의 요청을 허용할지 정책 설정
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )

    def include_router(self):
        self.app.include_router(check_server.router)
        self.app.include_router(test.router)


    def run(self):
        import uvicorn
        # uvicorn을 통해 fastapi 서버 실행

        uvicorn.run(self.app, host="0.0.0.0", port=8080)




my_app = FastAPIApp()


if __name__ == "__main__":
    my_app.include_router()
    my_app.run()
    