import selenium.webdriver
from selenium.webdriver.chrome.service import Service
import selenium.webdriver.remote
import selenium.webdriver.remote.webelement
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options   
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from typing import Literal
import selenium
import time

 
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

def get_text_by_xpath(driver:webdriver.Chrome, xpath:str):
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element.text
    except:
        return 'None'
    
def get_button(driver:webdriver.Chrome, path:str, by:Literal["xpath", "class_name"]):
    if by == "xpath":
        try:
            button = driver.find_element(By.XPATH, path)
        except:
            button = "None"
        return button
    elif by == "class_name":
        try:
            button = driver.find_element(By.CLASS_NAME, path)
        except:
            button = "None"
        return button


def open_new_tab(driver:webdriver.Chrome, button:selenium.webdriver.remote.webelement):
    ActionChains(driver).key_down(Keys.CONTROL).click(button).key_up(Keys.CONTROL).perform()


def scroll_to_end(driver:webdriver.Chrome):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # AJAX 로드 대기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # 더 이상 로드할 내용이 없음
            break
        last_height = new_height