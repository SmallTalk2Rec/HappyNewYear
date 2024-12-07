FROM --platform=linux/amd64 python:3.11.11-slim
# 리눅스 기반 python 환경 구축

RUN apt-get update -y
# 리눅스 패키지 설치 툴 update
RUN python -m pip install --upgrade pip
# python 패키지 설치 툴 update
RUN apt-get install -y --no-install-recommends apt-utils
# apt 관련 추가 유틸리티 기능 설치
RUN apt-get -y install curl
RUN apt-get install -y telnet
# 통신 테스트를 위한 패키지 설치
RUN apt-get install libgomp1
# (OpenMP)병렬 처리를 지원하는 라이브러리를 설치

RUN apt-get clean 
RUN rm -rf /var/lib/apt/lists/*
# 필요 패키지 설치 이후 캐시 삭제


COPY requirements.txt ./
# python 패키지 리스트 파일 복사

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
# python 패키지 설치

WORKDIR /smalktalk2rec/FastAPI
# 작업 폴더 설정

CMD ["/bin/bash"]
# 컨테이너 생성이 종료되지 않게 명령어 설정