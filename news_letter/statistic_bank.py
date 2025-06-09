from function_list.news_scraping_func import fetch_news_date
from function_list.basic_options import mongo_setting, selenium_setting, init_browser
from selenium.webdriver.common.by import By
from newspaper import Article
import time

def process_links(link_elements, collection, browser, link_list, crawling_count):
    """
    뉴스 링크를 처리하여 MongoDB에 저장합니다.

    Args:
        link_elements(List[str]): 뉴스 링크 요소 리스트
        collection(MongoDB Collection): MongoDB 컬렉션 객체
        browser(WebDriver): Selenium 브라우저 객체
        link_list(List[str]): 기존에 저장된 뉴스 링크 리스트
        crawling_count(int): 현재까지 크롤링된 데이터 개수

    Returns:
        crawling_count(int): 업데이트된 크롤링된 데이터 개수
    """
    for link_element in link_elements:
        link = link_element.get_attribute('href')
        if link not in link_list:  # 중복된 링크는 제외
            if link_element.text in ['관련 자료 보러 가기', '관련기사 보기']:
                time.sleep(1)  # 대기 시간
                try:
                    # 특정 도메인 필터링
                    if 'https://zdnet.co.kr/error/' in link or 'cuts.top' in link or \
                       'dailysecu' in link or 'datanet' in link or 'search.naver' in link or \
                       'kmib.co.kr' in link or 'cctvnews' in link:
                        pass  # 무시할 링크
                    else:
                        # 뉴스 기사 파싱
                        article = Article(link, language='ko')
                        article.download()
                        article.parse()
                        title, date, content = article.title, article.publish_date, article.text

                        # 제목 또는 본문이 없는 경우 추가 처리
                        if title is None or content is None or 'news.naver' in link or 'newsis.com' in link:
                            link_element.click()
                            browser.switch_to.window(browser.window_handles[-1])
                            try:
                                news_dict = fetch_news_date(link, browser)  # 추가 데이터 수집
                                news_dict['news_link'] = link
                            except:
                                pass
                            browser.close()
                            browser.switch_to.window(browser.window_handles[-1])

                        # 날짜가 없는 경우 추가 처리
                        elif date is None:
                            link_element.click()
                            browser.switch_to.window(browser.window_handles[-1])
                            try:
                                date = fetch_news_date(link, browser)
                            except:
                                pass
                            browser.close()
                            browser.switch_to.window(browser.window_handles[-1])
                            news_dict = {
                                'news_title': title,
                                'news_content': content,
                                'news_date': date,
                                'news_link': link,
                                'news_reference': 'statistic_bank'
                            }

                        # MongoDB에 데이터 저장
                        collection.insert_one(news_dict)
                        crawling_count += 1

                except:
                    pass  # 예외 발생 시 무시
    return crawling_count


def statistic_bank():
    """
    Statistic Bank 웹사이트에서 뉴스 데이터를 크롤링하여 MongoDB에 저장합니다.
    """
    crawling_count = 0  # 크롤링된 데이터 개수 초기화

    # MongoDB 컬렉션 설정
    mongo_client,collection = mongo_setting('news_scraping', 'news_list')

    # Selenium 브라우저 초기화
    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)

    # Statistic Bank 웹사이트 접속
    browser.get("https://page.stibee.com/archives/102448")

    # 메인 페이지에서 콘텐츠 리스트 가져오기
    contents_list = browser.find_elements(By.CSS_SELECTOR, '#stb_archives > div.stb_archives_body > div > a')

    # MongoDB에서 기존에 저장된 뉴스 링크 가져오기
    results = collection.find({}, {'_id': 0, 'news_link': 1})
    link_list = [i['news_link'] for i in results]

    for i in range(5):  # 최대 5개의 콘텐츠 처리
        time.sleep(1)
        link_element = contents_list[i].get_attribute('href')
        browser.get(link_element)  # 콘텐츠 링크로 이동

        time.sleep(1)

        # 첫 번째 링크 리스트를 가져와 처리
        link_list_1st = browser.find_elements(By.CSS_SELECTOR, 
                                              'body > div.public-email > div > table > tbody > tr > td > div > table > tbody > tr > td > table > tbody > tr > td > div > div.stb-text-box > table > tbody > tr > td > div > a')
        crawling_count = process_links(link_list_1st, collection, browser, link_list, crawling_count)

        # 두 번째 링크 리스트는 주석 처리됨
        # link_list_2nd = browser.find_elements(By.CSS_SELECTOR, 
        #                                       'body > div.public-email > div > table > tbody > tr > td > div > table > tbody > tr > td > table > tbody > tr > td > div > div > table > tbody > tr > td > table.stb-cell-wrap-cta > tbody > tr > td > a')
        # process_links(link_list_2nd, collection, browser)

        browser.back()  # 이전 페이지로 돌아감

    # 브라우저 종료
    browser.quit()
    print('statistic bank crawling finish')
    print('crawling count : ', crawling_count)
    mongo_client.close()
# 크롤링 함수 실행
# statistic_bank()
