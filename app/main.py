from app import my_app
from router.chat_router import chat_router
from router.common_router import common_router

from fastapi import FastAPI


def create_app() -> FastAPI:
    my_app.include_router(chat_router)  # 라우터를 포함시킵니다.
    my_app.include_router(common_router)
    return my_app.app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
