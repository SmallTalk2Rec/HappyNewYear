from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from tqdm import tqdm
import pickle
    
def get_driver(use_headless:bool=True, proxy_server:bool=None, chrome_driver_path:str=None) -> webdriver.Chrome:
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
    chrome_options.add_argument("--disable-build-check")
    
    if use_headless:
        chrome_options.add_argument('--headless=new')  # 최신 Chrome에서 안정적으로 작동
    
    if proxy_server:
        chrome_options.add_argument(f'--proxy-server={proxy_server}')

    if chrome_driver_path is None:
        # Chrome 드라이버를 자동으로 설정
        driver = Service(ChromeDriverManager.install())
    else:
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
    return driver



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


def get_text_by_xpath(driver:webdriver.Chrome, xpath:str):
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element.text
    except:
        return 'None'