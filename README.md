# HappyNewYear

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
streamlit run src/app.py --server.runOnSave true
```


## fastapi 카카오 서버 사용 방법
1. 공유된 pem 파일을 이용해 aws ec2 서버에 접속한다.
2. git branch를 cli에 실행해 현재 branch를 확인한다.(FastAPI-kakao-server)
3. 서버 branch임을 확인하고 sudo docker ps를 통해 서버 컨테이너 상태를 확인
4. sudo docker compose down을 통해 현재 실행중인 컨테이너 종료
4.1(Optional) git pull을 통해 FastAPI-kakao-server branch의 수정사항을 반영한다.
5. sudo docker compose up --build를 통해 새로운 컨테이너 실행
6. 해당 ec2 주소 8080포트의 fastapi docs로 이동 (http://3.35.15.244:8080/docs)
7. docs내 oauth/redirect_authorize_url api를 실행 -> 결과창의 주소로 이동
8. API 결과창의 주소로 이동
8.1 카카오톡 로그인 및 동의 절차 진행 및 웹브라우저에 null이 보이면 성공
10. 영화어떄 카카오톡에서 채팅을 쳐서 테스트 진행