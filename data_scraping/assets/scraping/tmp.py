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