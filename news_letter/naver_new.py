from function_list.basic_options import mongo_setting,selenium_setting,init_browser
from selenium.webdriver.common.by import By
import time
import pandas as pd
from news_preprocess.noun_extraction import ner_remove_in_text
from transformers import AutoTokenizer, logging, AutoModelForTokenClassification

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
                news_company = news_contents[i].find_element(by=By.CSS_SELECTOR,value='div.sa_text_info_left').text.split('\n')[0]
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
                    news_list.append(dict_news)
# 크롤링 함수 실행
def news_contents(collection,tokenizer,model):
    crawling_count = 0
    chrome_options = selenium_setting()
    news_list = collection.find({'noun_list': {'$exists': False}},{'_id': 1, 'news_link': 1})
    browser = init_browser(chrome_options)
    for i in news_list:
        browser.get(i['news_link'])
        try:
            news_date = browser.find_elements(by=By.CSS_SELECTOR,value='#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span')[-1].text
            news_date = news_date.replace('오후', 'PM').replace('오전', 'AM')
            news_date = pd.to_datetime(news_date, format='%Y.%m.%d. %p %I:%M')
        except:
            try:
                news_date = browser.find_elements(by=By.CSS_SELECTOR,value='#content > div.NewsEnd_container__HcfWh > div > div.NewsEnd_main_group__d5k8S > div > div.NewsEndMain_comp_article_head__Uqd6M > div.article_head_info > div.NewsEndMain_article_head_date_info__jGlzH > div> em')[-1].text
                news_date = news_date.replace('오후', 'PM').replace('오전', 'AM')
                news_date = pd.to_datetime(news_date, format='%Y.%m.%d. %p %I:%M')
            except:
                news_date = ''
        try:
            news_content_origin = browser.find_element(by=By.CSS_SELECTOR,value='#dic_area').text
        except:
            try:
                news_content_origin = browser.find_element(by=By.CSS_SELECTOR,value='#comp_news_article').text
            except:
                news_content_origin = ''

        if news_content_origin != '':
            noun_text = ner_remove_in_text(news_content_origin,model,tokenizer)
        else:
            noun_text = ''
        try:
            news_journalist = browser.find_element(by=By.CSS_SELECTOR,value='div.media_end_head_journalist > a').text.replace(' 기자','').split('\n')
        except:
            try:
                news_journalist = browser.find_element(by=By.CSS_SELECTOR,value='div.media_end_head_journalist > button').text.replace(' 기자','').split('\n')
            except:
                try:
                    news_journalist = browser.find_element(by=By.CSS_SELECTOR,value='em.NewsEndMain_name__lNckc').text.replace(' 기자','').split('\n')
                except:
                    news_journalist = []
        news_journalist = ', '.join(news_journalist)
        if noun_text == '':
            collection.update_one({'_id': i['_id']},  {'$set': {'news_date':news_date,'news_journalist':news_journalist,'noun_list':noun_text}})
            # collection.update_one({'_id': i['_id']},  {'$set': {'news_date':news_date,'news_content':news_content_origin,'news_journalist':news_journalist,'noun_list':noun_text}})
        crawling_count += 1
        pass
    print('naver news crawling finish')
    print('crawling count : ',crawling_count)
    pass

def duplicated_data_delete(collection):
    # Step 1: Aggregation으로 중복된 데이터 중 가장 오래된 _id를 찾기
    pipeline = [
        {
            "$group": {
                "_id": "$noun_list",  # news_content를 기준으로 그룹화
                "oldestId": {"$min": "$_id"},  # 가장 오래된 _id를 찾기
                "ids": {"$push": "$_id"}  # 모든 _id를 배열로 저장
            }
        },
        {
            "$project": {
                "_id": 1,
                "idsToDelete": {
                    "$filter": {
                        "input": "$ids",
                        "as": "id",
                        "cond": {"$ne": ["$$id", "$oldestId"]}  # oldestId를 제외한 나머지 _id
                    }
                }
            }
        }
    ]

    # Aggregation 실행
    duplicates = list(collection.aggregate(pipeline))

    # Step 2: 중복 데이터 삭제
    for doc in duplicates:
        if doc["idsToDelete"]:  # 삭제할 데이터가 있는 경우
            collection.delete_many({"_id": {"$in": doc["idsToDelete"]}})


def naver_news():
    collection = mongo_setting('news_scraping','naver_news')
    tokenizer = AutoTokenizer.from_pretrained("KPF/KPF-bert-ner")
    model = AutoModelForTokenClassification.from_pretrained("KPF/KPF-bert-ner")
    # link_list(collection)
    news_contents(collection,tokenizer,model)
    duplicated_data_delete(collection)
