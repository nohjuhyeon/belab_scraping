from function_list.basic_options import mongo_setting,selenium_setting,init_browser
from selenium.webdriver.common.by import By
import time
import pandas as pd
def link_list(collection):
    link_dict = collection.find({},{'_id':0,'news_link':1})
    link_list = [i['news_link'] for i in link_dict]
    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)
    pass
    browser.get("https://news.naver.com/section/105")    
    section_list = browser.find_elements(by=By.CSS_SELECTOR,value='#ct_wrap > div.ct_scroll_wrapper > div.column0 > div > ul > li > a')
    news_list = []
    for j in range(len(section_list)):
        section_list = browser.find_elements(by=By.CSS_SELECTOR,value='#ct_wrap > div.ct_scroll_wrapper > div.column0 > div > ul > li > a')
        section_link = section_list[j].get_attribute('href')
        browser.get(section_link)
        section_name = browser.find_element(by=By.CSS_SELECTOR,value='h3.section_title_h').text
        if section_name != '게임/리뷰':
            finish_check =False
            while True:
                news_contents = browser.find_elements(by=By.CSS_SELECTOR,value='div.sa_text')
                news_date = news_contents[-1].find_elements(by=By.CSS_SELECTOR,value='div')[1].text.split('\n')[1]
                news_link = news_contents[-1].find_element(by=By.CSS_SELECTOR,value='a')
                news_link = news_link.get_attribute('href')
                if news_date in ['3일전','4일전','5일전','6일전','7일전'] or news_link in link_list:
                    break
                else:
                    plus_btn = browser.find_elements(by=By.CSS_SELECTOR,value='#newsct > div.section_latest > div > div.section_more > a')
                    if finish_check == True:
                        break
                    elif len(plus_btn) != 0:
                        plus_btn[0].click()
                        time.sleep(1)
            news_contents = browser.find_elements(by=By.CSS_SELECTOR,value='div.sa_text')
            for i in range(len(news_contents)):
                news_title = news_contents[i].find_element(by=By.CSS_SELECTOR,value='a > strong').text
                news_content = news_contents[i].find_element(by=By.CSS_SELECTOR,value='div.sa_text_lede').text
                news_company = news_contents[i].find_element(by=By.CSS_SELECTOR,value='div.sa_text_info_left').text
                news_date = news_contents[i].find_element(by=By.CSS_SELECTOR,value='div.sa_text_info_right').text
                news_link = news_contents[i].find_element(by=By.CSS_SELECTOR,value='a')
                news_link = news_link.get_attribute('href')

                if news_date == '3일전':
                    break
                elif news_link in link_list:
                    pass
                else:
                    link_list.append(news_link)
                    dict_news = {'news_title':news_title,'news_part_content':news_content,'news_company':news_company,'news_date':news_date,'news_link':news_link,'section_type':section_name}
                    collection.insert_one(dict_news)
                    print(dict_news)
                    news_list.append(dict_news)
# 크롤링 함수 실행
def news_contents(collection):
    crawling_count = 0
    chrome_options = selenium_setting()
    news_list = collection.find({'news_content': {'$exists': False}},{'_id': 1, 'news_link': 1})
    browser = init_browser(chrome_options)
    for i in news_list:
        browser.get(i['news_link'])
        news_date = browser.find_elements(by=By.CSS_SELECTOR,value='#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span')[-1].text
        news_date = news_date.replace('오후', 'PM').replace('오전', 'AM')
        news_date = pd.to_datetime(news_date, format='%Y.%m.%d. %p %I:%M')

        news_content_origin = browser.find_element(by=By.CSS_SELECTOR,value='#dic_area').text
        try:
            news_journalist = browser.find_element(by=By.CSS_SELECTOR,value='div.media_end_head_journalist > a').text.replace(' 기자','').split('\n')
        except:
            try:
                news_journalist = browser.find_element(by=By.CSS_SELECTOR,value='div.media_end_head_journalist > button').text.replace(' 기자','').split('\n')
            except:
                news_journalist = []
        news_journalist = ', '.join(news_journalist)
        collection.update_one({'_id': i['_id']},  {'$set': {'news_date':news_date,'news_content':news_content_origin,'news_journalist':news_journalist}})
        crawling_count += 1
        pass
    print('naver news crawling finish')
    print('crawling count : ',crawling_count)
    pass

def naver_news():
    collection = mongo_setting('news_scraping','naver_news')

    link_list(collection)
    news_contents(collection)
