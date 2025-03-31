# 웹 크롤링 동작
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd 
from selenium.webdriver.common.by import By
from function_list.basic_options import mongo_setting, selenium_setting, init_browser

def news_collection(browser, collection, title_list, crawling_count):
    """
    뉴스 데이터를 크롤링하여 MongoDB에 저장합니다.

    Args:
        browser(WebDriver): Selenium WebDriver 객체.
        collection(MongoDB Collection): MongoDB 컬렉션 객체.
        title_list(List[str]): 이미 저장된 뉴스 제목 리스트.
        crawling_count(int): 현재까지 크롤링된 뉴스 개수.

    Returns:
        crawling_count(int): 업데이트된 크롤링된 뉴스 개수.
    """
    # 뉴스 목록과 페이지 목록 가져오기
    news_list = browser.find_elements(By.CSS_SELECTOR, '#main > div.search-feed > div > div > div.story-card.story-card--art-left.|.flex.flex--wrap.box--hidden-sm > div.story-card-right.|.grid__col--sm-8.grid__col--md-8.grid__col--lg-8.box--pad-left-xs > div.story-card__headline-container.|.box--margin-bottom-xs > div > a')
    page_list = browser.find_elements(By.CSS_SELECTOR, '#main > div.parent.|.flex.flex--justify-center.flex--align-items-center > div.number > ul > li')

    # 페이지별 크롤링
    for j in range(len(page_list)):
        time.sleep(1)
        page_list = browser.find_elements(By.CSS_SELECTOR, '#main > div.parent.|.flex.flex--justify-center.flex--align-items-center > div.number > ul > li')
        page_list[j].click()  # 페이지 클릭
        element_body = browser.find_element(By.CSS_SELECTOR, "body")
        element_body.send_keys(Keys.HOME)  # 페이지 맨 위로 이동
        time.sleep(1)

        # 뉴스 목록 재로드
        news_list = browser.find_elements(By.CSS_SELECTOR, '#main > div.search-feed > div > div > div.story-card.story-card--art-left.|.flex.flex--wrap.box--hidden-sm > div.story-card-right.|.grid__col--sm-8.grid__col--md-8.grid__col--lg-8.box--pad-left-xs > div.story-card__headline-container.|.box--margin-bottom-xs > div > a')
        scrapping_finish = False

        # 뉴스 상세 정보 크롤링
        for i in range(len(news_list)):
            time.sleep(1)
            news_list = browser.find_elements(By.CSS_SELECTOR, '#main > div.search-feed > div > div > div.story-card.story-card--art-left.|.flex.flex--wrap.box--hidden-sm > div.story-card-right.|.grid__col--sm-8.grid__col--md-8.grid__col--lg-8.box--pad-left-xs > div.story-card__headline-container.|.box--margin-bottom-xs > div > a')
            time.sleep(2)

            # 뉴스 링크 및 상세 정보 가져오기
            news_link = news_list[i].get_attribute('href')
            news_list[i].click()
            time.sleep(1)
            news_title = browser.find_element(By.CSS_SELECTOR, '#fusion-app > div.article > div:nth-child(2) > div > div > div.article-header__headline-container.|.box--pad-left-md.box--pad-right-md > h1 > span').text
            news_content = browser.find_element(By.CSS_SELECTOR, '#fusion-app > div.article > div:nth-child(2) > div > section > article > section').text
            news_date = browser.find_elements(By.CSS_SELECTOR, '#fusion-app > div.article > div:nth-child(2) > div > section > article > div.article-dateline.|.flex.flex--justify-space-between.flex--align-items-top.box--border.box--border-grey-40.box--border-horizontal.box--border-horizontal-bottom.box--pad-bottom-sm > span > span')[-1].text.split()[1]
            news_date = pd.to_datetime(news_date)

            # 중복 뉴스 확인
            if news_title in title_list:
                scrapping_finish = True
                browser.back()
                break
            else:
                # MongoDB에 뉴스 데이터 저장
                collection.insert_one({
                    'news_title': news_title,
                    'news_content': news_content,
                    'news_date': news_date,
                    'news_link': news_link,
                    'news_reference': 'venture_doctors'
                })
                crawling_count += 1
                browser.back()

        time.sleep(2)
        if scrapping_finish:
            break

    browser.quit()
    return crawling_count


def venture_doctors():
    """
    '벤처하는 의사들' 키워드로 뉴스 데이터를 크롤링하여 MongoDB에 저장합니다.
    """
    crawling_count = 0

    # MongoDB 설정
    collection = mongo_setting('news_scraping', 'news_list')

    # Selenium 설정 및 브라우저 초기화
    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)

    # 웹사이트 접속
    browser.get("https://biz.chosun.com/nsearch/?query=%5B%EB%B2%A4%EC%B2%98%ED%95%98%EB%8A%94%20%EC%9D%98%EC%82%AC%EB%93%A4%5D&page=1&siteid=chosunbiz&sort=1&date_period=all&date_start=&date_end=&writer=&field=&emd_word=&expt_word=&opt_chk=true&app_check=0&website=chosunbiz&category=")
    time.sleep(3)

    # 기존 뉴스 제목 리스트 가져오기
    title_list = [i['news_title'] for i in collection.find({}, {'news_title': 1, '_id': 0})]

    # 뉴스 크롤링 수행
    crawling_count = news_collection(browser, collection, title_list, crawling_count)

    # 크롤링 결과 출력
    print('venture_doctors crawling finish')
    print('crawling count:', crawling_count)
