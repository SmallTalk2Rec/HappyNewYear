# 테이블 명세

## custom_movie_rating
- 설명: 사용자가 영화 평가한 데이터   
- columns:  
    - "CustomID": 고객번호
    - "MovieID": 영화번호 
    - "MovieName": 영화이름 
    - "Rating": 고객이 남긴 평점   
- 개수 (241206) : 85891

## movie_info
- 설명: 왓챠피디아에 나와있는 영화정보
- columns: 
    - "MovieID": 영화번호
    - "Title": 제목
    - "Year": 연도
    - "Genre": 장르
    - "Country": 국가
    - "Runtime": 상영시간
    - "Age": 제한연령 (None이면 전체)
    - "Cast_Production_Info_List": 감독, 배우들 
    - "Synopsis": 시놉시스 
    - "Avg_Rating": 평균평점
    - "N_Rating(만명)": 평점수
    - "N_Comments": 리뷰 수
- 개수 (241206) : 3005

## movie_comments
- 설명: 영화에 남긴 리큐 데이터
- columns: 
    - "MovieID": 영화번호
    - "CustomID": 고객번호
    - "Comment": 리뷰
    - "Rating": 평점
    - "N_Likes": 리뷰가 받은 좋아요 수
- 개수 (241206) : 56391