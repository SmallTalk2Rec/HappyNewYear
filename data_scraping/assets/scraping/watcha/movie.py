from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from assets.utils.driver import get_text_by_xpath, scroll_to_end, get_button, open_new_tab
from assets.utils.re import time_to_minutes, extract_movie_age, extract_number

def separate_cast(cast_list):
    main_cast = []  # 주연 리스트
    supporting_cast = []  # 조연 리스트

    for item in cast_list:
        if '주연' in item:
            # 주연 항목에서 이름만 추출 (이름은 '\n' 앞에 있음)
            name = item.split('\n')[0]
            main_cast.append(name)
        elif '조연' in item:
            # 조연 항목에서 이름만 추출 (이름은 '\n' 앞에 있음)
            name = item.split('\n')[0]
            supporting_cast.append(name)

    return main_cast, supporting_cast

def get_movie_url(driver:webdriver.Chrome, movie_name:str) -> str:
    url = f'https://pedia.watcha.com/ko-KR/search?query={movie_name}'
    driver.get(url)
    time.sleep(1)

    # 팝업 창 뜨면 없애기
    try:
        driver.find_element(By.CLASS_NAME, "hsDVweTz").click()
    except:
        pass
    time.sleep(1)

    # 가장 첫번째 창 클릭
    driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/section/section/div[2]/div[1]/section/section[2]/div[1]/ul/li[1]/a/div[1]/div[1]').click()
    time.sleep(1)

    movie_url = driver.current_url

    return movie_url


def get_customer_id(driver:webdriver.Chrome, xpath:str) -> str:
    button = get_button(driver, xpath, by='xpath')
    
    open_new_tab(driver, button)
    
    # 모든 탭 확인
    tabs = driver.window_handles

    # 새 탭으로 전환
    driver.switch_to.window(tabs[1])
    
    movie_id = driver.current_url.split('/')[-1]
    
    # 작업 후 새 탭 닫기
    driver.close()
    
    # 원래 탭으로 전환
    driver.switch_to.window(tabs[0])

    return movie_id


def get_watch_infos(driver:webdriver.Chrome, movie_id:str, n_comment:int = 10) -> dict:
    """
    driver : chrome driver
    n_comment : 코멘트 개수
    movie_id : 영화의 url id
    
    return: {
    title : 영화 제목
    moive_info : 영화정보 (연도, 장르, 제작국가)
    movie_info_2 : 영화정보 (상영시간, 제한연령)
    cast_production_info_list : 출연/제작 정보, 감독, 배우 정보
    movie_synopsis : 영화 요약 소개
    avg_rating : 평균 평점
    avg_rating_n : 평점 남긴 숫자
    comments_list: 커멘트 list {'custom_id':custom_id, 'comment':comment, 'rating':rating, 'n_likes':n_likes}
    }
    """
    watcha_infos = {}
    watcha_infos['describe'] = """
    
    """

    url = f'https://pedia.watcha.com/ko-KR/contents/{movie_id}'
    driver.get(url)

    time.sleep(1)

    # 팝업 창 뜨면 없애기
    try:
        get_button(driver, "hsDVweTz", by='class_name').click()
        time.sleep(1)

    except:
        pass
        

    # 제목
    watcha_infos['title'] = get_text_by_xpath(driver, '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/h1')
    time.sleep(0.1)

    # 영화정보 (연도, 장르, 제작국가)
    tmp = get_text_by_xpath(driver,  '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[2]').split('·')
    time.sleep(0.1)
    year, genre, country = [item.strip() for item in tmp]
    watcha_infos['year'] = year
    watcha_infos['genre'] = genre
    watcha_infos['country'] = country
    
    
    # 영화정보2 (런타임, 연령)
    tmp  = get_text_by_xpath(driver,  '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[3]').split('·')
    time.sleep(0.1)
    runtime, age = [item.strip() for item in tmp]
    runtime = time_to_minutes(runtime)
    age = extract_movie_age(age)

    watcha_infos['runtime'] = runtime
    watcha_infos['age'] = age



    # 출연/제작 정보
    i = 1
    cast_production_info_list = []

    while True:
        cast_production_info_xpath = f'//*[@id="content_credits"]/section/div[1]/ul/li[{i}]/a/div[2]'
        cast_production_info = get_text_by_xpath(driver, cast_production_info_xpath)
        time.sleep(0.1)

        if cast_production_info != 'None':
            cast_production_info_list.append(cast_production_info)
            i += 1
        else:
            break

    main_cast, sup_cast = separate_cast(cast_production_info_list)
    watcha_infos['main_cast'] = main_cast
    watcha_infos['sup_cast'] = sup_cast

    # 영화 내용 소개
    movie_synopsis_xpath = '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section/div[2]/section[2]/p' 
    watcha_infos['movie_synopsis'] = get_text_by_xpath(driver, movie_synopsis_xpath)
    time.sleep(0.1)

    # 평균평점
    avg_rating_xpath = '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[2]/section[1]/div[2]/div/div[1]'
    watcha_infos['avg_rating'] = get_text_by_xpath(driver, avg_rating_xpath)
    time.sleep(0.1)
    
    # 평점수
    n_rating_xpath = '//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[1]/section/span/strong'
    n_rating = extract_number(get_text_by_xpath(driver, n_rating_xpath))
    watcha_infos['avg_rating_n'] = n_rating
    time.sleep(0.1)
    
    # 코멘트 수
    n_comments = extract_number(get_text_by_xpath(driver, '/html/body/div[1]/div[1]/section/div/div[2]/section/section[2]/header/span'))
    watcha_infos['n_comments'] = n_comments

    # 왓챠피디아 코멘트 더보기 url
    url = f'https://pedia.watcha.com/ko-KR/contents/{movie_id}/comments'
    driver.get(url)
    time.sleep(1)

    # comments
    # 1. 스크롤 내려줘야 10개이상 볼 수 있음
    # 2. '보기' 눌러줘야 함
    
    scroll_to_end(driver)
    
    comments_list = []
    
    i = 1
    while True:
        if n_comment is not None:
            if i > n_comment:
                break
                        
        try:
            comment_button_xpath = f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[2]/a/div/span/button'
            get_button(driver, comment_button_xpath, by='xpath').click()
            time.sleep(0.1)
        except:
            pass
        
        try:
            custom_id = get_customer_id(driver, f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[1]/div[1]/a/div[2]') # 제목
            time.sleep(0.1)
            comment = get_text_by_xpath(driver, f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[2]/a/div/div') # 내용
            time.sleep(0.1)
            rating = get_text_by_xpath(driver, f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[1]/div[2]/span ') # 별점
            time.sleep(0.1)
            n_likes = get_text_by_xpath(driver, f'//*[@id="root"]/div[1]/section/section/div/div/div/ul/div[{i}]/div[3]/em[1]') # 좋아요 수
            time.sleep(0.1)
            
            comments_list.append({'custom_id':custom_id, 'comment':comment, 'rating':rating, 'n_likes':n_likes})
            
            i += 1
        except Exception as e:
            print(e)
            break
        
    watcha_infos['comments_list'] = comments_list
    
    return watcha_infos