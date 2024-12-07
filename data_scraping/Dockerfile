# 1. 베이스 이미지로 Python 3.10 사용
FROM --platform=linux/amd64 python:3.10-slim

# 2. 작업 디렉터리 설정
WORKDIR /app

# 3. 필요한 패키지 설치를 위한 requirements.txt 복사
COPY requirements.txt .

# 4. 필요한 Python 패키지 설치
# 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    curl \    
    unzip \
    gnupg \
    gnupg2 \
    gnupg1 \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    default-jdk \
    && apt-get clean

# Chrome 브라우저 설치
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# ChromeDriver 설치
RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

RUN pip install --no-cache-dir -r requirements.txt