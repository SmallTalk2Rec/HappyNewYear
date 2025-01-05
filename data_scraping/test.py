from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from lxml import etree
import time

movie_url = "https://pedia.watcha.com/ko-KR/contents/tRzL8nV"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    page = context.new_page()
    page.goto(movie_url, timeout=600000)

    try:
        button_selector = (
            'button.hsDVweTz[type="button"]:has-text("3일 동안 보지 않기")'
        )

        button = page.locator(button_selector)
        button.click(force=True)
    except Exception as e:
        print(e)

    # 출연/제작 정보
    cast_production_info_list = []

    while True:
        content = page.content()

        soup = BeautifulSoup(content, "html.parser")
        tree = etree.HTML(str(soup))

        i = 1
        while True:
            try:
                name = tree.xpath(
                    f'//*[@id="content_credits"]/section/div[1]/ul/li[{i}]/a/div[2]/div[1]/div[1]/text()'
                )[0].replace("/", " ")
                role = tree.xpath(
                    f'//*[@id="content_credits"]/section/div[1]/ul/li[{i}]/a/div[2]/div[1]/div[2]/text()'
                )[0].replace("/", " ")
                unique_id = (
                    page.locator(
                        f'//*[@id="content_credits"]/section/div[1]/ul/li[{i}]/a'
                    )
                    .get_attribute("href")
                    .split("/")[-1]
                )

                cast_production_info_list.append((name, role, unique_id))
                i += 1
            except Exception:
                break

        button_selector = '//*[@id="content_credits"]/section/div[2]/button'
        button = page.locator(button_selector)

        if button.count() > 0:  # 버튼이 존재하는지 확인
            try:
                button.click(force=True)

            except Exception:
                break
        else:
            break

print(cast_production_info_list)

# browser.close()
