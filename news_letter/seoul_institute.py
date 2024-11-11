# * 웹 크롤링 동작
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager
webdriver_manager_directory = ChromeDriverManager().install()
import time
import os 
# ChromeDriver 실행

from selenium.webdriver.chrome.options import Options

from pymongo import MongoClient
import pandas as pd 
from selenium.webdriver.common.by import By          # - 정보 획득

def init_browser():
    # Chrome 브라우저 옵션 생성
    chrome_options = Options()

    # User-Agent 설정
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    # 다운로드 폴더 설정

    # 추가적인 Chrome 옵션 설정 (특히 Docker 환경에서 필요할 수 있음)
    chrome_options.add_argument('--headless')  # GUI 없는 환경에서 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')  # GPU 사용 안함

    # WebDriver 생성
    webdriver_manager_directory = ChromeDriverManager().install()
    service = ChromeService(webdriver_manager_directory)

    # User-Agent 설정

    # WebDriver 생성

    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser


def research_report(browser,link_list,collection,crawling_count):
    finish_check = False

    while True:
        contents_list = browser.find_elements(by=By.CSS_SELECTOR,value='#center > article > div > div > div.view-content > div > ul > li div > h2 > a')
        for i in range(len(contents_list)):
            contents_list = browser.find_elements(by=By.CSS_SELECTOR,value='#center > article > div > div > div.view-content > div > ul > li div > h2 > a')
            news_link = contents_list[i].get_attribute('href')
            contents_list[i].click()
            time.sleep(1)
            news_title = browser.find_element(by=By.CSS_SELECTOR,value='div#center > article > div > div > h2').text
            news_date = browser.find_element(by=By.CSS_SELECTOR,value='div.content.clearfix > div.common_info > div:nth-child(1) > div.field-items > div').text
            news_date = pd.to_datetime(news_date)
            news_content = browser.find_element(by=By.CSS_SELECTOR,value='div.content.clearfix > div.field.field-name-field-summary.field-type-text-with-summary.field-label-hidden > div > div').text
            keywords = browser.find_elements(by=By.CSS_SELECTOR,value='div.content.clearfix > div.field.field-name-field-tags.field-type-taxonomy-term-reference.field-label-inline.clearfix > div.field-items > div > a')
            keywords_list = [i.text for i in keywords]
            if news_date.year >= 2023 and news_link not in link_list:
                collection.insert_one({'news_title': news_title,
                                        'news_content': news_content,
                                        'news_date': news_date,
                                        'news_link': news_link,
                                        'keywords':keywords_list,
                                        'news_subject':'서울연구보고서'

                                    })
                browser.back()
                crawling_count += 1
                time.sleep(1)
            else:
                finish_check = True
                break
        if finish_check == True:
            break
        else:
            next_btn = browser.find_element(by=By.CSS_SELECTOR,value='#center > article > div > div > div.item-list > ul > li.pager-next > a')
            next_btn.click()
            time.sleep(1)
    browser.quit()                                      # - 브라우저 종료
    return crawling_count
            
def world_trends(browser,link_list,collection,crawling_count):
    finish_check = False

    while True:
        time.sleep(1)
        book_list = browser.find_elements(by=By.CSS_SELECTOR,value='#container_suite > div.view-side-left > ul > li > a')
        for j in range(len(book_list)):
            time.sleep(1)
            element_body = browser.find_element(by=By.CSS_SELECTOR,value="body")    
            element_body.send_keys(Keys.HOME)
            time.sleep(1)
            book_list = browser.find_elements(by=By.CSS_SELECTOR,value='#container_suite > div.view-side-left > ul > li > a')
            book_list[j].click()
            time.sleep(1)
            contents_list = browser.find_elements(by=By.CSS_SELECTOR,value='#container_suite > div.view-side-right > div > div > ul > li > div > h2 > a')
            for i in range(1,len(contents_list)):
                contents_list = browser.find_elements(by=By.CSS_SELECTOR,value='#container_suite > div.view-side-right > div > div > ul > li > div > h2 > a')
                news_link = contents_list[i].get_attribute('href')
                contents_list[i].click()
                time.sleep(1)
                news_title = browser.find_element(by=By.CSS_SELECTOR,value='div#center > article > div > div > h2').text
                news_date = browser.find_element(by=By.CSS_SELECTOR,value='div.content.clearfix > div.common_info > div:nth-child(1) > div.field-items > div').text
                news_date = pd.to_datetime(news_date)
                news_content = browser.find_element(by=By.CSS_SELECTOR,value='div.content.clearfix > div.field.field-name-field-summary.field-type-text-with-summary.field-label-hidden > div > div').text
                if news_date.year >= 2023 and news_link not in link_list:
                    collection.insert_one({'news_title': news_title,
                                            'news_content': news_content,
                                            'news_date': news_date,
                                            'news_link': news_link,
                                            'news_subject':'세계도시동향'
                                        })
                    browser.back()
                    crawling_count += 1
                    time.sleep(1)
                else:
                    finish_check = True
                    break
            if finish_check == True:
                break
        if finish_check == True:
            break
        
        else:
            next_btn = browser.find_element(by=By.CSS_SELECTOR,value='#center > article > div > div > div.item-list > ul > li.pager-next > a')
            next_btn.click()
            time.sleep(1)

        time.sleep(1)
    return crawling_count

def seoul_institute(): 
    crawling_count = 0
    mongo_url = os.environ.get("DATABASE_URL")
    mongo_client = MongoClient(mongo_url)
    # database 연결
    database = mongo_client["news_scraping"]
    # collection 작업
    collection = database['seoul_institute']

    results = collection.find({},{'_id':0,'news_link':1})
    link_list = [i['news_link'] for i in results]

    pass
    browser = init_browser()
    browser.get("https://www.si.re.kr/research_report")                                     # - 주소 입력
    crawling_count = research_report(browser,link_list,collection,crawling_count)
    browser = init_browser()
    browser.get("https://www.si.re.kr/world_trends")                                     # - 주소 입력
    crawling_count = world_trends(browser,link_list,collection,crawling_count)
    print('seoul institute crawling finish')
    print('crawling count : ',crawling_count)
                                                        # - 가능 여부에 대한 OK 받음
    pass

# seoul_institute()