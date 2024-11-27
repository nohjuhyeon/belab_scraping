from function_list.ict_scraping_func import fetch_news_date
from function_list.basic_options import mongo_setting,selenium_setting,init_browser
from selenium.webdriver.common.by import By
from newspaper import Article
import time

def process_links(link_elements, collection, browser,link_list,crawling_count):
    for link_element in link_elements:
        link = link_element.get_attribute('href')
        if link not in link_list:
            if link_element.text in ['관련 자료 보러 가기','관련기사 보기']:
                time.sleep(1)  # 대기 시간
                try:
                    if 'https://zdnet.co.kr/error/' in link or 'cuts.top' in link  or 'dailysecu' in link or 'datanet' in link or 'search.naver' in link or 'kmib.co.kr' in link or 'cctvnews' in link:
                        pass  # 해당 링크는 무시            
                    else:
                        article = Article(link, language='ko')
                        article.download()
                        article.parse()
                        title, date, content = article.title, article.publish_date, article.text
                        
                        if title is None or content is None:
                            link_element.click()
                            browser.switch_to.window(browser.window_handles[-1])
                            try:
                                news_dict = fetch_news_date(link, browser)
                                news_dict['news_link']=link
                            except:
                                pass
                            browser.close()
                            browser.switch_to.window(browser.window_handles[-1])

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
                                'news_reference':'statistic_bank'
                            }
                        collection.insert_one(news_dict)
                        crawling_count+=1

                except:
                    pass
    return crawling_count


def statistic_bank():
    crawling_count = 0
    # MongoDB 클라이언트 및 컬렉션 설정
    crawling_count = 0
    collection = mongo_setting('news_scraping','news_list')
    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)

    # 브라우저 초기화 및 사이트 접속
    browser.get("https://page.stibee.com/archives/102448")
    
    # 메인 페이지에서 콘텐츠 리스트를 가져옴
    contents_list = browser.find_elements(By.CSS_SELECTOR, '#stb_archives > div.stb_archives_body > div > a')
    results = collection.find({},{'_id':0,'news_link':1})
    link_list = [i['news_link'] for i in results]

    for i in range(5):
        time.sleep(1)
        contents_list[i].click()
        browser.switch_to.window(browser.window_handles[-1])
        time.sleep(1)

        # 첫 번째 링크 리스트를 가져와 처리
        link_list_1st = browser.find_elements(By.CSS_SELECTOR, 'body > div.public-email > div > table > tbody > tr > td > div > table > tbody > tr > td > table > tbody > tr > td > div > div.stb-text-box > table > tbody > tr > td > div > a')
        crawling_count = process_links(link_list_1st, collection, browser,link_list,crawling_count)

        # # 두 번째 링크 리스트를 가져와 처리
        # link_list_2nd = browser.find_elements(By.CSS_SELECTOR, 'body > div.public-email > div > table > tbody > tr > td > div > table > tbody > tr > td > table > tbody > tr > td > div > div > table > tbody > tr > td > table.stb-cell-wrap-cta > tbody > tr > td > a')
        # process_links(link_list_2nd, collection, browser)

        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        
    # 브라우저 종료
    browser.quit()
    print('statistic bank crawling finish')
    print('crawling count : ',crawling_count)

# 크롤링 함수 실행
# statistic_bank()
