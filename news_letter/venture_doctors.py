# * 웹 크롤링 동작
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager
webdriver_manager_directory = ChromeDriverManager().install()
import time
# ChromeDriver 실행
import pandas as pd 
from selenium.webdriver.chrome.options import Options

from pymongo import MongoClient  
import os 

def venture_doctors():
        crawling_count = 0
        mongo_url = os.getenv("DATABASE_URL")
        mongo_client = MongoClient(mongo_url)
        # database 연결
        database = mongo_client["news_scraping"]
        # collection 작업
        collection = database['venture_doctors']
        # Chrome 브라우저 옵션 생성
        chrome_options = Options()

        # User-Agent 설정
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

        # WebDriver 생성
        webdriver_manager_dricetory = ChromeDriverManager().install()

        browser = webdriver.Chrome(service = ChromeService(webdriver_manager_directory), options=chrome_options)                        # - chrome browser 열기

        # Chrome WebDriver의 capabilities 속성 사용
        capabilities = browser.capabilities

        pass
        browser.get("https://biz.chosun.com/nsearch/?query=%5B%EB%B2%A4%EC%B2%98%ED%95%98%EB%8A%94%20%EC%9D%98%EC%82%AC%EB%93%A4%5D&page=1&siteid=chosunbiz&sort=1&date_period=all&date_start=&date_end=&writer=&field=&emd_word=&expt_word=&opt_chk=true&app_check=0&website=chosunbiz&category=")                                     # - 주소 입력

                                                        # - 가능 여부에 대한 OK 받음
        pass
        html = browser.page_source                          # - html 파일 받음(and 확인)
        # print(html)

        from selenium.webdriver.common.by import By          # - 정보 획득
        # browser.save_screenshot('./formats.png')           
        title_list = [i['news_title'] for i in collection.find({},{'news_title':1,'_id':0})]
        time.sleep(3)
        news_list = browser.find_elements(by=By.CSS_SELECTOR,value='#main > div.search-feed > div > div > div.story-card.story-card--art-left.\|.flex.flex--wrap.box--hidden-sm > div.story-card-right.\|.grid__col--sm-8.grid__col--md-8.grid__col--lg-8.box--pad-left-xs > div.story-card__headline-container.\|.box--margin-bottom-xs > div > a')
        page_list = browser.find_elements(by=By.CSS_SELECTOR,value='#main > div.parent.\|.flex.flex--justify-center.flex--align-items-center > div.number > ul > li')
        for j in range(len(page_list)):
                time.sleep(1)
                page_list = browser.find_elements(by=By.CSS_SELECTOR,value='#main > div.parent.\|.flex.flex--justify-center.flex--align-items-center > div.number > ul > li')
                page_list[j].click()
                element_body = browser.find_element(by=By.CSS_SELECTOR,value="body")    
                element_body.send_keys(Keys.HOME)
                time.sleep(1)
                news_list = browser.find_elements(by=By.CSS_SELECTOR,value='#main > div.search-feed > div > div > div.story-card.story-card--art-left.\|.flex.flex--wrap.box--hidden-sm > div.story-card-right.\|.grid__col--sm-8.grid__col--md-8.grid__col--lg-8.box--pad-left-xs > div.story-card__headline-container.\|.box--margin-bottom-xs > div > a')
                scrapping_finsih = False
                for i in range(len(news_list)):
                        time.sleep(1)
                        news_list = browser.find_elements(by=By.CSS_SELECTOR,value='#main > div.search-feed > div > div > div.story-card.story-card--art-left.\|.flex.flex--wrap.box--hidden-sm > div.story-card-right.\|.grid__col--sm-8.grid__col--md-8.grid__col--lg-8.box--pad-left-xs > div.story-card__headline-container.\|.box--margin-bottom-xs > div > a')
                        time.sleep(2)
                        news_link = news_list[i].get_attribute('href')
                        news_list[i].click()
                        time.sleep(1)
                        news_title = browser.find_element(by=By.CSS_SELECTOR,value='#fusion-app > div.article > div:nth-child(2) > div > div > div.article-header__headline-container.\|.box--pad-left-md.box--pad-right-md > h1 > span').text
                        news_content = browser.find_element(by=By.CSS_SELECTOR,value='#fusion-app > div.article > div:nth-child(2) > div > section > article > section').text
                        news_date = browser.find_elements(by=By.CSS_SELECTOR,value='#fusion-app > div.article > div:nth-child(2) > div > section > article > div.article-dateline.\|.flex.flex--justify-space-between.flex--align-items-top.box--border.box--border-grey-40.box--border-horizontal.box--border-horizontal-bottom.box--pad-bottom-sm > span > span')[-1].text.split()[1]
                        news_date = pd.to_datetime(news_date)
                        if news_title in title_list:
                                scrapping_finsih = True
                                browser.back()
                                break
                        else:
                                collection.insert_one({'news_title':news_title,
                                        'news_content':news_content,
                                        'news_date': news_date,
                                        'news_link':news_link})
                                crawling_count += 1
                                browser.back()
                time.sleep(2)
                if scrapping_finsih == True:
                        break
                                
        browser.quit()                                      # - 브라우저 종료
        print('venture_doctors crawling finish')
        print('crawling count : ',crawling_count)
# venture_doctors()