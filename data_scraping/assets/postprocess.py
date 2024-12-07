from assets.utils import *

def get_movie_info(movie_name, movie_id, watcha_infos, naver_infos, wiki_infos):
    # 후처리
    movie_info = {}
    movie_info['describe'] = """
    *** 왓챠 추출 ***
    movie_name : 검색한 영화 제목 (str)
    movie_id : 왓챠 영화 id (str)
    title : 왓챠 영화 제목 (str)
    synopsis : 영화 요약 소개
    year : 연도 (str)
    genre : 장르 (str)
    country : 국가 (str)
    runtime : 상영시간 (str)
    age : 제한연령 (str) , 전체이용가는 12세로 처리
    main_cast : 주연 (list)
    sup_cast : 조연 (list)
    avg_rating : 평균평점 (str)
    avg_rating_n : 평점수 (str)
    comments : 커멘트 (list), [Dict{유저이름, 평점, 좋아요 수, 이유, 답글 수}, Dict, ...]
    
    *** 네이버 추출 ***
    total_audience : 총 관객수 , 만명단위 , 영화진흥위원회 통합 전산망 데이터로 업데이트 되고 있다고 함. 2005년도 전은 없음.
    channel : 상영된 OTT
    
    *** 위치 추출 ***
    writer: 각본
    producer: 제작
    dp: 촬영
    original_story: 원작
    editor: 편집
    music_director: 음악
    production_company: 제작사
    distribution_company: 배급사
    production_budget: 제작비
    box_office_revenue: 흥행수익
    language: 언어
    """
    movie_info['movie_name'] = movie_name
    movie_info['movie_id'] = movie_id 
    movie_info['movie_title'] = watcha_infos['title']
    movie_info['synopsis'] = watcha_infos['movie_synopsis']

    # 왓챠 후처리
    tmp = watcha_infos['movie_info'].split('·')
    year, genre, country = [item.strip() for item in tmp]

    movie_info['year'] = year
    movie_info['genre'] = genre
    movie_info['country'] = country

    tmp = watcha_infos['movie_info_2'].split('·')
    runtime, age = [item.strip() for item in tmp]
    runtime = time_to_minutes(runtime)

    age = extract_movie_age(age)
    movie_info['runtime'] = runtime
    movie_info['age'] = age

    main_cast, sup_cast = separate_cast(watcha_infos['cast_production_info_list'])
    movie_info['main_cast'] = main_cast
    movie_info['sup_cast'] = sup_cast

    movie_info['avg_rating'] = watcha_infos['avg_rating']
    movie_info['avg_rating_n'] = extract_number(watcha_infos['avg_rating_n'])

    movie_info['comments'] = watcha_infos['comments_list']

    # 네이버 후처리    
    movie_info['channel'] = naver_infos.get('채널', None)
    total_n = naver_infos.get('관객수', None)
    if not total_n:
        movie_info['total_audience'] = None
    else:
        movie_info['total_audience'] = extract_number(total_n)

    # 위키 후처리
    movie_info['writer'] = wiki_infos['movie_info'].get('각본', None)
    movie_info['producer'] = wiki_infos['movie_info'].get('제작', None)
    movie_info['dp'] = wiki_infos['movie_info'].get('촬영', None)
    movie_info['original_story'] = wiki_infos['movie_info'].get('원작', None)
    movie_info['editor'] = wiki_infos['movie_info'].get('편집', None)
    movie_info['music_director'] = wiki_infos['movie_info'].get('음악', None)
    movie_info['production_company'] = wiki_infos['movie_info'].get('제작사', None)
    movie_info['distribution_company'] = wiki_infos['movie_info'].get('배급사', None)
    movie_info['production_budget'] = wiki_infos['movie_info'].get('제작비', None)
    movie_info['box_office_revenue'] = wiki_infos['movie_info'].get('흥행수익', None)
    movie_info['language'] = wiki_infos['movie_info'].get('언어', None)

    return movie_info