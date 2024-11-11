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
def seoul_institute():
    crawling_count = 0
    mongo_url = os.getenv("DATABASE_URL")
    mongo_client = MongoClient(mongo_url)
    # database 연결
    database = mongo_client["news_scraping"]
    # collection 작업
    collection = database['seoul_institute']
    # Chrome 브라우저 옵션 생성
    chrome_options = Options()

    # User-Agent 설정
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    # WebDriver 생성
    webdriver_manager_dricetory = ChromeDriverManager().install()

    browser = webdriver.Chrome(service = ChromeService(webdriver_manager_directory), options=chrome_options)                        # - chrome browser 열기

    # Chrome WebDriver의 capabilities 속성 사용
    capabilities = browser.capabilities
    from selenium.webdriver.common.by import By          # - 정보 획득
    # browser.save_screenshot('./formats.png')           
    import pandas as pd 

    pass
    browser.get("https://www.si.re.kr/research_report")                                     # - 주소 입력

                                                        # - 가능 여부에 대한 OK 받음
    pass
    html = browser.page_source                          # - html 파일 받음(and 확인)
    # print(html)
    results = collection.find({},{'_id':0,'news_link':1})
    link_list = [i['news_link'] for i in results]
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
            
    finish_check = False
    world_content_list = browser.find_element(by=By.CSS_SELECTOR,value='#block-system-main-menu > div > ul > li:nth-child(2) > a')
    world_content_list.click()

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

    browser.quit()                                      # - 브라우저 종료
    print('seoul institute crawling finish')
    print('crawling count : ',crawling_count)

# seoul_institute()