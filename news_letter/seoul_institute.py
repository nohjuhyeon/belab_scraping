from selenium.webdriver.common.keys import Keys
from function_list.basic_options import selenium_setting,init_browser
import time
import pandas as pd 
from selenium.webdriver.common.by import By          # - 정보 획득
from function_list.basic_options import mongo_setting

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
                                        'news_subject':'서울연구보고서'})
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
    collection = mongo_setting('news_scraping','seoul_institute')

    results = collection.find({},{'_id':0,'news_link':1})
    link_list = [i['news_link'] for i in results]

    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)

    browser.get("https://www.si.re.kr/research_report")                                     # - 주소 입력
    crawling_count = research_report(browser,link_list,collection,crawling_count)

    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)

    browser.get("https://www.si.re.kr/world_trends")                                     # - 주소 입력
    crawling_count = world_trends(browser,link_list,collection,crawling_count)
    print('seoul institute crawling finish')
    print('crawling count : ',crawling_count)
                                                        # - 가능 여부에 대한 OK 받음
    pass

# seoul_institute()