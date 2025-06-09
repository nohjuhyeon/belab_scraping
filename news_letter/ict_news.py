from function_list.news_scraping_func import fetch_news_date
from function_list.basic_options import mongo_setting, selenium_setting, init_browser
from selenium.webdriver.common.by import By
from newspaper import Article
import time
from selenium.webdriver.common.keys import Keys

def process_links(link_elements, collection, browser, news_topic, crawling_count):
    """
    링크 리스트를 처리하여 뉴스 데이터를 크롤링하고 MongoDB에 저장합니다.

    Args:
        link_elements(List[str]): 뉴스 링크 요소 리스트
        collection(MongoDB Collection): MongoDB 컬렉션 객체
        browser(WebDriver): Selenium 브라우저 객체
        news_topic(str): 뉴스 주제
        crawling_count(int): 현재까지 크롤링된 뉴스 개수

    Returns:
        crawling_count(int): 업데이트된 크롤링된 뉴스 개수
    """
    # 기존에 저장된 뉴스 링크 가져오기
    results = collection.find({}, {'_id': 0, 'news_link': 1})
    link_list = [i['news_link'] for i in results]
    original_window = browser.current_window_handle  # 현재 브라우저 창 핸들 저장

    for link_element in link_elements:
        link = link_element.get_attribute('href')  # 링크 URL 추출
        time.sleep(1)  # 대기 시간

        if link not in link_list:  # 중복되지 않은 링크만 처리
            try:
                # 특정 URL 패턴 제외
                if any(x in link for x in ['https://zdnet.co.kr/error/', 'cuts.top', 'dailysecu', 'datanet', 
                                           'search.naver', 'kmib.co.kr', 'cctvnews']):
                    continue

                # 뉴스 데이터를 Article 라이브러리로 처리
                article = Article(link, language='ko')
                article.download()
                article.parse()
                title, date, content = article.title, article.publish_date, article.text

                # 제목 또는 내용이 없는 경우 추가 처리
                if title is None or content is None or 'news.naver' in link or 'newsis.com' in link:
                    link_element.click()
                    browser.switch_to.window(browser.window_handles[-1])  # 새 창으로 전환
                    try:
                        news_dict = fetch_news_date(link, browser)
                        news_dict['news_topic'] = news_topic
                        news_dict['news_link'] = link
                    except:
                        pass
                    browser.close()
                    browser.switch_to.window(original_window)

                # 날짜가 없는 경우 처리
                elif date is None:
                    link_element.click()
                    browser.switch_to.window(browser.window_handles[-1])  # 새 창으로 전환
                    try:
                        date = fetch_news_date(link, browser)
                    except:
                        pass
                    browser.close()
                    browser.switch_to.window(original_window)

                    # 뉴스 데이터 생성
                    news_dict = {
                        'news_title': title,
                        'news_content': content,
                        'news_date': date,
                        'news_link': link,
                        'news_topic': news_topic,
                        'news_reference': 'ict_news'
                    }
                    collection.insert_one(news_dict)  # MongoDB에 데이터 저장
                    crawling_count += 1  # 크롤링 카운트 증가
            except:
                pass

        # 열린 모든 창 닫기
        for handle in browser.window_handles:
            if handle != original_window:
                browser.switch_to.window(handle)
                browser.close()
        browser.switch_to.window(original_window)  # 원래 창으로 복귀

    return crawling_count


def ict_news():
    """
    ICT 뉴스 웹사이트에서 뉴스 데이터를 크롤링하여 MongoDB에 저장하는 함수.
    """
    crawling_count = 0  # 크롤링된 뉴스 개수 초기화
    mongo_client,collection = mongo_setting('news_scraping', 'news_list')  # MongoDB 컬렉션 설정
    chrome_options = selenium_setting()  # Selenium 브라우저 옵션 설정
    browser = init_browser(chrome_options)  # 브라우저 초기화

    # ICT 뉴스 클리핑 페이지 접속
    browser.get("https://ictnewsclipping.stibee.com/")
    time.sleep(1)

    # 첫 번째 콘텐츠 링크로 이동
    first_content = browser.find_element(by=By.CSS_SELECTOR, value='#__next > div > div > div:nth-child(1) > a')
    first_link = first_content.get_attribute('href')
    browser.get(first_link)
    time.sleep(1)

    for j in range(5):  # 5번 반복하며 뉴스 크롤링
        time.sleep(1)
        # 뉴스 콘텐츠와 제목 가져오기
        content_list_first = browser.find_elements(by=By.CSS_SELECTOR, value='div.stb-left-cell > div.stb-text-box > table > tbody > tr > td')
        content_title = browser.find_elements(by=By.CSS_SELECTOR, value='#__next > div:nth-child(1) > div > div > div')[0].text

        if '[ICT 뉴스' in content_title:  # 제목에 '[ICT 뉴스'가 포함된 경우만 처리
            for i in content_list_first:
                try:
                    news_topic = i.find_element(by=By.CSS_SELECTOR, value='div > span').text
                except:
                    news_topic = i.find_element(by=By.CSS_SELECTOR, value='h2 > span').text
                contents_list = i.find_elements(by=By.CSS_SELECTOR, value='a')
                crawling_count = process_links(contents_list, collection, browser, news_topic, crawling_count)
        else:
            j -= 1  # 올바른 뉴스 제목이 아닐 경우 반복 횟수 감소

        # 페이지 스크롤 및 이전 버튼 클릭
        body = browser.find_element(by=By.TAG_NAME, value='body')
        body.send_keys(Keys.END)
        time.sleep(1)
        try:
            alarm_btn = browser.find_element(by=By.CSS_SELECTOR, value='button.no-subscription')
            alarm_btn.click()
        except:
            pass
        time.sleep(2)
        before_btn = browser.find_element(by=By.CSS_SELECTOR, value='div.prev')
        before_btn.click()

    browser.quit()  # 브라우저 종료
    print('ict news crawling finish')  # 크롤링 완료 메시지 출력
    print('crawling count : ', crawling_count)  # 크롤링된 뉴스 개수 출력
    mongo_client.close()