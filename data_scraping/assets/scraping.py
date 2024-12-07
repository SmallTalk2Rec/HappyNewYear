from selenium import webdriver
from selenium.webdriver.common.by import By
from assets.utils import *

# 왓챠
def get_watch_infos(driver:webdriver.Chrome, movie_id:str, n_comment:int = 10) -> dict:
    """
    driver : chrome driver
    n_comment : 코멘트 개수
    movie_id : 영화의 url id
    """
    watcha_infos = {}
    watcha_infos['describe'] = """
    title : 영화 제목
    moive_info : 영화정보 (연도, 장르, 제작국가)
    movie_info_2 : 영화정보 (상영시간, 제한연령)
    cast_production_info_list : 출연/제작 정보, 감독, 배우 정보
    movie_synopsis : 영화 요약 소개
    avg_rating : 평균 평점
    avg_rating_n : 평점 남긴 숫자
    comments_list: 커멘트 list
    """

    url = f'https://pedia.watcha.com/ko-KR/contents/{movie_id}'
    driver.get(url)

    time.sleep(1)

    # 팝업 창 뜨면 없애기
    try:
        driver.find_element(By.CLASS_NAME, "hsDVweTz").click()
    except:
        pass
        
    time.sleep(1)


    # 제목
    title_xpath = '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/h1'
    watcha_infos['title'] = get_text_by_xpath(driver, title_xpath)

    # 영화정보 (연도, 장르, 제작국가)
    movie_info_xpath = '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[2]'
    watcha_infos['movie_info'] = get_text_by_xpath(driver, movie_info_xpath)
    
    # 영화정보2 (런타임, 연령)
    movie_info_xpath_2 = '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[3]'
    watcha_infos['movie_info_2'] = get_text_by_xpath(driver, movie_info_xpath_2)


    # 출연/제작 정보
    i = 1
    cast_production_info_list = []

    while True:
        cast_production_info_xpath = f'//*[@id="content_credits"]/section/div[1]/ul/li[{i}]/a/div[2]'
        cast_production_info = get_text_by_xpath(driver, cast_production_info_xpath)

        if cast_production_info != 'None':
            cast_production_info_list.append(cast_production_info)
            i += 1
        else:
            break

    watcha_infos['cast_production_info_list'] = cast_production_info_list

    # 영화 내용 소개
    movie_synopsis_xpath = '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section/div[2]/section[2]/p' 
    watcha_infos['movie_synopsis'] = get_text_by_xpath(driver, movie_synopsis_xpath)

    # 평균평점
    avg_rating_xpath = '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[2]/section[1]/div[2]/div/div[1]'
    watcha_infos['avg_rating'] = get_text_by_xpath(driver, avg_rating_xpath)

    # 평점수
    avg_rating_xpath_n_xpath = '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[1]/section/span/strong'
    watcha_infos['avg_rating_n'] = get_text_by_xpath(driver, avg_rating_xpath_n_xpath)

    # 왓챠피디아 기생충 코멘트 더보기 url
    url = f'https://pedia.watcha.com/ko-KR/contents/{movie_id}/comments'
    driver.get(url)

    # JavaScript로 페이지 끝까지 스크롤
    # 한번 스크롤하면 약 9개이상 증가함
    for _ in range(int(n_comment / 9) + 1):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    # comments
    # 1. 스크롤 내려줘야 10개이상 볼 수 있음
    # 2. '보기' 눌러줘야 함
    comments_list = []
    for i in range(1, n_comment+1):                
        comment_button_xpath = f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[2]/a/div/span/button'
        if get_text_by_xpath(driver, comment_button_xpath) == '보기':
            try:
                driver.find_element(By.XPATH,comment_button_xpath).click()
            except:
                continue
        
        title = get_text_by_xpath(driver, f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[1]/div[1]/a/div[2]') # 제목
        comment = get_text_by_xpath(driver, f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[2]/a/div/div') # 내용
        rating = get_text_by_xpath(driver, f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[1]/div[2]/span ') # 별점
        n_likes = get_text_by_xpath(driver, f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[3]/em[1]') # 좋아요 수
        
        comments_list.append({'title':title, 'comment':comment, 'rating':rating, 'n_likes':n_likes})
        
    watcha_infos['comments_list'] = comments_list
    
    return watcha_infos

# 네이버 검색
def get_naver_infos(driver:webdriver.Chrome, movie_name:str) -> dict:
    naver_infos = {}
    naver_infos['describe'] = """
    개요 : 장르, 나라, 시간
    개봉 : 개봉일
    평점 : 네이버 평점
    관객수 or 채널
    """

    url = f'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={movie_name}'
    driver.get(url)
    time.sleep(1)


    # 관객수
    i = 1
    while True:
        key_xpath = f'//*[@id="main_pack"]/div[3]/div[2]/div[1]/div/div[1]/dl/div[{i}]/dt'
        value_xpath = f'//*[@id="main_pack"]/div[3]/div[2]/div[1]/div/div[1]/dl/div[{i}]/dd'
        key = get_text_by_xpath(driver, key_xpath)
        value = get_text_by_xpath(driver, value_xpath)
        
        if value != 'None':
            naver_infos[key] = value
            i += 1
        else:
            break
    
    if len(naver_infos) == 1:
        # 한번 더 시도
        i = 1
        while True:
            key_xpath = f'//*[@id="main_pack"]/div[3]/div[2]/div[2]/div/div[1]/dl/div[{i}]/dt'
            value_xpath = f'//*[@id="main_pack"]/div[3]/div[2]/div[2]/div/div[1]/dl/div[{i}]/dd'
            key = get_text_by_xpath(driver, key_xpath)
            value = get_text_by_xpath(driver, value_xpath)
            
            if value != 'None':
                naver_infos[key] = value
                i += 1
            else:
                break
            
    return naver_infos

# 위키검색
def get_wiki_infos(driver:webdriver.Chrome, movie_name:str) -> dict:
    def get_movie_info(url):
        driver.get(url)
        time.sleep(1)

        # 영화정보
        movie_info = {}
        i = 2

        # 2가지 경우가 있음
        while True:
            key_xpath = f'//*[@id="mw-content-text"]/div[1]/table[2]/tbody/tr[{i+1}]/th'
            value_xpath = f'//*[@id="mw-content-text"]/div[1]/table[2]/tbody/tr[{i+1}]/td'

            key = get_text_by_xpath(driver, key_xpath)
            value = get_text_by_xpath(driver, value_xpath)
            
            if value != 'None':
                movie_info[key] = value
                i += 1
            else:
                break
        
        # 한번 더 시도
        if len(movie_info) == 0:        
            while True:
                key_xpath = f'//*[@id="mw-content-text"]/div[1]/table/tbody/tr[{i+1}]/th'
                value_xpath = f'//*[@id="mw-content-text"]/div[1]/table/tbody/tr[{i+1}]/td'

                key = get_text_by_xpath(driver, key_xpath)
                value = get_text_by_xpath(driver, value_xpath)
                
                if value != 'None':
                    movie_info[key] = value
                    i += 1
                else:
                    break
            
        return movie_info
        
    wiki_infos = {}
    wiki_infos['describe'] = """
    movie_info : 영화정보 (각본, 제작, 촬영, 편집, 음악, 제작사, 배급사, 개봉일, 시간, 국가, 언어)
    """
    
    # 2가지 버전으로 검색
    # '인턴 (영화)'검색 안되면  '인턴'로 검색해야함
    url = f'https://ko.wikipedia.org/wiki/{movie_name} (영화)'

    movie_info = get_movie_info(url)
    if len(movie_info) == 0:
        url = f'https://ko.wikipedia.org/wiki/{movie_name}'
        
        movie_info = get_movie_info(url)

    wiki_infos['movie_info'] = movie_info

    return wiki_infos