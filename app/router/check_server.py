from fastapi import APIRouter
from starlette.responses import Response
import datetime, pytz

router = APIRouter()

@router.get("/")
async def index():
    """
    '상태 체크용 API'\n
    :return:
    """
    kr_timezone = pytz.timezone('Asia/Seoul')
    current_time = datetime.datetime.now(kr_timezone)
    return Response(f"samlltalk2rec server API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")