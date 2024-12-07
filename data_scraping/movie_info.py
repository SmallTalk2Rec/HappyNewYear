from lxml import html
from assets.utils.re import extract_number
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from lxml import etree

def get_data(movie_id):
    movie_url = f"https://pedia.watcha.com/ko-KR/contents/{movie_id}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(movie_url)
        
        # 모든 스크롤이 완료된 후 콘텐츠 가져오기
        content = page.content()
        browser.close()
     
    # 3. BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(content, 'html.parser')

    # 4. BeautifulSoup 객체를 lxml로 변환
    tree = etree.HTML(str(soup))

    # XPath를 사용해 데이터 추출
    try:
        title = tree.xpath('//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/h1/text()')[0].replace('/', '')
    except:
        time.sleep(3)
        try:
            title = tree.xpath('//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/h1/text()')[0].replace('/', '')
        except: 
            title = None
    try:
        movie_info = tree.xpath('//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[2]/text()')[0].replace('/', '').split('·')
        year, genre, country = [item.strip() for item in movie_info]
    except:
        year, genre, country = None, None, None
    
    try:
        movie_info2 = tree.xpath('//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[1]/div[2]/div/div[3]/text()')[0].replace('/', '').split('·')
        if len(movie_info2) == 1:
            runtime = [item.strip() for item in movie_info2][0]
            age = None
        else:
            runtime, age = [item.strip() for item in movie_info2]
    except:
        runtime, age = None, None
            
    # 출연/제작 정보
    i = 1
    cast_production_info_list = []

    while True:
        try:
            name = tree.xpath(f'//*[@id="content_credits"]/section/div[1]/ul/li[{i}]/a/div[2]/div[1]/div[1]/text()')[0].replace('/', '')
            role = tree.xpath(f'//*[@id="content_credits"]/section/div[1]/ul/li[{i}]/a/div[2]/div[1]/div[2]/text()')[0].replace('/', '_')
            
            cast_production_info_list.append((name, role))
            i += 1
        except Exception as e:
            break
    
    try:
        synopsis = tree.xpath('//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[2]/section[3]/p/text()')[0].replace('\n', ' ').replace('/', '')
    except:
        synopsis = None
    try:
        avg_rating = tree.xpath('//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[2]/section[1]/div[2]/div/div[1]/text()')[0]
    except:
        avg_rating = None
    try:
        n_rating = extract_number(tree.xpath('//*[@id="root"]/div[1]/section/div/div[2]/div/div/div[2]/section[1]/div[2]/section[1]/div[2]/div/div[2]/text()')[1])
    except:
        n_rating = None
    try:
        n_comments = tree.xpath('/html/body/div[1]/div[1]/section/div/div[2]/section/section[2]/header/span/text()')[0]
    except:
        n_comments = None
    return [title, year, genre, country, runtime, age, cast_production_info_list, synopsis, avg_rating, n_rating, n_comments]


if __name__ == "__main__":
    import pandas as pd
    from assets.utils.txt import append_to_txt
    import time

    # print(get_data("mZ5em95"))
    
    # 지정할 열 이름
    column_names = ["CustomID", "MovieID", "MovieName", "Rating"]

    # 데이터 읽기
    df = pd.read_csv('./data/custom_movie_rating.txt', sep='/', header=None, names=column_names, encoding='utf-8')
    
    for i, movie_id in enumerate(df['MovieID'].tolist()):
        print(f"{i} / {df.shape[0]}", end='\r')  # '\r'로 줄을 덮어씀
        movie_info = get_data(movie_id)
        append_to_txt("./data/movie_info_watcha.txt", [movie_id, *movie_info])
