from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app import my_app
from auth.kakao_auth import auto_refresh_token

import os

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")  # 발급받은 Access Token
KAKAO_REDIRECT_URL = os.getenv("KAKAO_REDIRECT_URL")

common_router = APIRouter()


@common_router.get("/oauth/redirect_authorize_url")
async def kakao_login():
    """
    Kakao Authorization URL로 리다이렉트.
    """
    authorization_url = f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_REST_API_KEY}&redirect_uri={KAKAO_REDIRECT_URL}/oauth&response_type=code"
    return RedirectResponse(authorization_url)  ## 디버깅 필요
    # return authorization_url


@common_router.get("/oauth")
def kakao_oauth_api(request: Request):
    """
    Kakao Authorizaion code 입력받아 access token 및 refresh token 받기
    """
    kakao_authorization_code = request.query_params.get("code")

    auto_refresh_token(my_app, kakao_authorization_code)
    print("kakao accesstoken complete")
