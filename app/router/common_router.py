from fastapi import APIRouter
from fastapi.responses import RedirectResponse

import os

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")  # 발급받은 Access Token
KAKAO_REDIRECT_URL = os.getenv("KAKAO_REDIRECT_URL")

common_router = APIRouter()


@common_router.get("/oauth/redirect_authorize_url")
async def kakao_login():
    """
    Kakao Authorization URL로 리다이렉트.
    """
    authorization_url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        f"client_id={KAKAO_REST_API_KEY}&redirect_uri={KAKAO_REDIRECT_URL}&response_type=code"
    )
    return RedirectResponse(authorization_url)


# @common_router.get("oauth")
# def oauth_api():
