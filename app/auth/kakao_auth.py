import os
import requests

ACCESS_TOKEN = os.getenv("KAKAO_ACCESS_TOKEN")  # 발급받은 Access Token
REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URL")
KAKAO_AUTHORIZATION_CODE = os.getenv("KAKAO_AUTHORIZATION_CODE")
TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"


def get_access_token(authorization_code, app):
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
        app.token_info["access_token"] = token_data.get("access_token")
        app.token_info["expires_in"] = token_data.get("expires_in", 0)

        # Refresh Token이 갱신되었을 경우 업데이트
        if "refresh_token" in token_data:
            app.token_info["refresh_token"] = token_data["refresh_token"]

        print("Access Token이 성공적으로 갱신되었습니다.")
    else:
        print("토큰 갱신 실패:", response.json())
        raise Exception("Failed to refresh Access Token")


def auto_refresh_token(app):
    """
    Access Token의 만료 시간을 확인하고 필요시 자동으로 갱신합니다.
    """
    if app.token_info["expires_in"] <= 0:
        print("Access Token 만료. 갱신 중...")
        get_access_token(KAKAO_AUTHORIZATION_CODE)
