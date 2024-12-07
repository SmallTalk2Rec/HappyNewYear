from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from tqdm import tqdm
import pickle

def save_file_to_pickle(file:str, file_path:str):
    """
    file: 저장할 파일
    file_path: 저장할 이름 (~.pkl)
    """
    # pickle 파일로 저장
    with open(file_path, 'wb') as f:  # 'wb'는 write binary의 약자
        pickle.dump(file, f)
        
def load_file_from_pickle(file_path:str):
    # pickle 파일에서 데이터 불러오기
    with open(file_path, 'rb') as f:  # 'rb'는 read binary의 약자
        file = pickle.load(f)
        
    return file

def get_text_by_xpath(driver:webdriver.Chrome, xpath:str):
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element.text
    except:
        return 'None'
    
def get_driver(use_headless:bool=True, proxy_server=None) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')  # GPU 비활성화
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')  # 확장 프로그램 비활성화
    chrome_options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,  # 이미지 비활성화
        "profile.default_content_setting_values.notifications": 2,  # 알림 비활성화
        "profile.default_content_setting_values.media_stream": 2,  # 미디어 스트림 비활성화
    })
    
    if use_headless:
        chrome_options.add_argument('--headless=new')  # 최신 Chrome에서 안정적으로 작동
    
    if proxy_server:
        chrome_options.add_argument(f'--proxy-server={proxy_server}')

    # Chrome 드라이버를 자동으로 설정
    service = Service(ChromeDriverManager().install())

    # Chrome 드라이버 로드
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

import re

# 2시간22 -> 144
def time_to_minutes(time_str: str) -> int:
    # '시간'과 '분' 앞에 있는 숫자를 추출하는 정규식
    hours_match = re.search(r'(\d+)시간', time_str)
    minutes_match = re.search(r'(\d+)분', time_str)

    # 추출한 '시간'과 '분' 값을 int로 변환 (없을 경우 0으로 처리)
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0

    # 시간을 분으로 변환한 값과 분을 더해줌
    total_minutes = hours * 60 + minutes
    
    return total_minutes

def extract_number(text: str) -> float:
    # 정규식을 이용해 숫자 부분만 추출
    match = re.search(r'(\d+\.\d+|\d+)', text)
    
    if match:
        return float(match.group(0))
    else:
        return None
    
def extract_movie_age(text: str) -> str:
    if '전체' == text:
        return '12'
    else:
        extract_number(text)
    
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

def get_movie_url(driver, movie_name:str) -> str:
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