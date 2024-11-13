# * 웹 크롤링 동작
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd 
from selenium.webdriver.common.by import By          # - 정보 획득
from function_list.basic_options import mongo_setting,selenium_setting,init_browser

def news_collection(browser,collection,title_list,crawling_count):
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
        browser.quit()                                      
        return crawling_count

def venture_doctors():
        crawling_count = 0
        collection = mongo_setting('news_scraping','venture_doctors')
        chrome_options = selenium_setting()
        browser = init_browser(chrome_options)
        pass
        browser.get("https://biz.chosun.com/nsearch/?query=%5B%EB%B2%A4%EC%B2%98%ED%95%98%EB%8A%94%20%EC%9D%98%EC%82%AC%EB%93%A4%5D&page=1&siteid=chosunbiz&sort=1&date_period=all&date_start=&date_end=&writer=&field=&emd_word=&expt_word=&opt_chk=true&app_check=0&website=chosunbiz&category=")                                     # - 주소 입력

        title_list = [i['news_title'] for i in collection.find({},{'news_title':1,'_id':0})]
        time.sleep(3)
        crawling_count = news_collection(browser,collection,title_list,crawling_count)
        print('venture_doctors crawling finish')
        print('crawling count : ',crawling_count)
