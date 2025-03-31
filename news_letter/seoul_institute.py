from selenium.webdriver.common.keys import Keys
from function_list.basic_options import selenium_setting, init_browser
import time
import pandas as pd
from selenium.webdriver.common.by import By
from function_list.basic_options import mongo_setting

def research_report(browser, link_list, collection, crawling_count):
    """
    서울연구원 연구보고서 데이터를 크롤링하여 MongoDB에 저장합니다.

    Args:
        browser(WebDriver): Selenium 브라우저 객체
        link_list(List[str]): 기존에 저장된 뉴스 링크 리스트
        collection(MongoDB Collection): MongoDB 컬렉션 객체
        crawling_count(int): 현재까지 크롤링된 데이터 개수

    Returns:
        crawling_count(int): 업데이트된 크롤링된 데이터 개수
    """
    finish_check = False  # 크롤링 종료 조건 초기화

    while True:
        # 보고서 리스트 가져오기
        contents_list = browser.find_elements(by=By.CSS_SELECTOR, value='#center > article > div > div > div.view-content > div > ul > li div > h2 > a')
        for i in range(len(contents_list)):
            contents_list = browser.find_elements(by=By.CSS_SELECTOR, value='#center > article > div > div > div.view-content > div > ul > li div > h2 > a')
            news_link = contents_list[i].get_attribute('href')
            contents_list[i].click()
            time.sleep(1)

            # 보고서 상세 정보 수집
            news_title = browser.find_element(by=By.CSS_SELECTOR, value='div#center > article > div > div > h2').text
            news_date = browser.find_element(by=By.CSS_SELECTOR, value='div.content.clearfix > div.common_info > div:nth-child(1) > div.field-items > div').text
            news_date = pd.to_datetime(news_date)
            news_content = browser.find_element(by=By.CSS_SELECTOR, value='div.content.clearfix > div.field.field-name-field-summary.field-type-text-with-summary.field-label-hidden > div > div').text
            keywords = browser.find_elements(by=By.CSS_SELECTOR, value='div.content.clearfix > div.field.field-name-field-tags.field-type-taxonomy-term-reference.field-label-inline.clearfix > div.field-items > div > a')
            category = browser.find_element(by=By.CSS_SELECTOR, value='div.textformatter-list').text.split(', ')
            keywords_list = [keyword.text for keyword in keywords]

            # 조건에 따라 데이터 저장
            if news_date.year >= 2023 and news_link not in link_list:
                collection.insert_one({
                    'news_title': news_title,
                    'news_content': news_content,
                    'news_date': news_date,
                    'news_link': news_link,
                    'keywords': keywords_list,
                    'category': category,
                    'news_subject': '서울연구보고서',
                    'news_reference': 'seoul_institute'
                })
                browser.back()
                crawling_count += 1
                time.sleep(1)
            else:
                finish_check = True
                break

        if finish_check:  # 종료 조건 확인
            break
        else:
            # 다음 페이지 버튼 클릭
            next_btn = browser.find_element(by=By.CSS_SELECTOR, value='#center > article > div > div > div.item-list > ul > li.pager-next > a')
            next_btn.click()
            time.sleep(1)

    browser.quit()  # 브라우저 종료
    return crawling_count


def world_trends(browser, link_list, collection, crawling_count):
    """
    서울연구원 세계도시동향 데이터를 크롤링하여 MongoDB에 저장합니다.

    Args:
        browser(WebDriver): Selenium 브라우저 객체
        link_list(List[str]): 기존에 저장된 뉴스 링크 리스트
        collection(MongoDB Collection): MongoDB 컬렉션 객체
        crawling_count(int): 현재까지 크롤링된 데이터 개수

    Returns:
        crawling_count(int): 업데이트된 크롤링된 데이터 개수
    """
    finish_check = False  # 크롤링 종료 조건 초기화

    while True:
        time.sleep(1)
        # 세계도시동향 보고서 리스트 가져오기
        book_list = browser.find_elements(by=By.CSS_SELECTOR, value='#container_suite > div.view-side-left > ul > li > a')
        for j in range(len(book_list)):
            time.sleep(1)
            element_body = browser.find_element(by=By.CSS_SELECTOR, value="body")
            element_body.send_keys(Keys.HOME)  # 페이지 상단으로 이동
            time.sleep(1)
            book_list = browser.find_elements(by=By.CSS_SELECTOR, value='#container_suite > div.view-side-left > ul > li > a')
            book_list[j].click()
            time.sleep(1)

            # 보고서 상세 정보 수집
            contents_list = browser.find_elements(by=By.CSS_SELECTOR, value='#container_suite > div.view-side-right > div > div > ul > li > div > h2 > a')
            for i in range(1, len(contents_list)):
                contents_list = browser.find_elements(by=By.CSS_SELECTOR, value='#container_suite > div.view-side-right > div > div > ul > li > div > h2 > a')
                news_link = contents_list[i].get_attribute('href')
                contents_list[i].click()
                time.sleep(1)

                # 보고서 상세 정보 수집
                news_title = browser.find_element(by=By.CSS_SELECTOR, value='div#center > article > div > div > h2').text
                news_date = browser.find_element(by=By.CSS_SELECTOR, value='div.content.clearfix > div.common_info > div:nth-child(1) > div.field-items > div').text
                news_date = pd.to_datetime(news_date)
                news_content = browser.find_element(by=By.CSS_SELECTOR, value='div.content.clearfix > div.field.field-name-field-summary.field-type-text-with-summary.field-label-hidden > div > div').text

                # 조건에 따라 데이터 저장
                if news_date.year >= 2023 and news_link not in link_list:
                    collection.insert_one({
                        'news_title': news_title,
                        'news_content': news_content,
                        'news_date': news_date,
                        'news_link': news_link,
                        'category': ['세계도시동향'],
                        'news_subject': '세계도시동향',
                        'news_reference': 'seoul_institute'
                    })
                    browser.back()
                    crawling_count += 1
                    time.sleep(1)
                else:
                    finish_check = True
                    break

            if finish_check:  # 종료 조건 확인
                break

        if finish_check:  # 종료 조건 확인
            break
        else:
            # 다음 페이지 버튼 클릭
            next_btn = browser.find_element(by=By.CSS_SELECTOR, value='#center > article > div > div > div.item-list > ul > li.pager-next > a')
            next_btn.click()
            time.sleep(1)

        time.sleep(1)
    return crawling_count


def seoul_institute():
    """
    서울연구원의 연구보고서와 세계도시동향 데이터를 크롤링하여 MongoDB에 저장합니다.
    """
    crawling_count = 0  # 크롤링된 데이터 개수 초기화
    collection = mongo_setting('news_scraping', 'report_list')  # MongoDB 컬렉션 설정

    # 기존에 저장된 뉴스 링크 가져오기
    results = collection.find({}, {'_id': 0, 'news_link': 1})
    link_list = [i['news_link'] for i in results]

    # 연구보고서 크롤링
    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)
    browser.get("https://www.si.re.kr/research_report")  # 연구보고서 페이지 접속
    crawling_count = research_report(browser, link_list, collection, crawling_count)

    # 세계도시동향 크롤링
    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)
    browser.get("https://www.si.re.kr/world_trends")  # 세계도시동향 페이지 접속
    crawling_count = world_trends(browser, link_list, collection, crawling_count)

    print('seoul institute crawling finish')
    print('crawling count : ', crawling_count)
