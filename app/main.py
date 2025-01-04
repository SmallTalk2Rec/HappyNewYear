from app import my_app
from app.router.chat_router import router

from fastapi import FastAPI


def create_app() -> FastAPI:
    my_app.include_router(router)  # 라우터를 포함시킵니다.
    return my_app.app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
