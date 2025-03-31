from function_list.basic_options import mongo_setting, selenium_setting, init_browser
from selenium.webdriver.common.by import By
import time
import pandas as pd
from news_preprocess.noun_extraction import ner_remove_in_text
from transformers import AutoTokenizer, AutoModelForTokenClassification

def link_list(collection):
    """
    네이버 뉴스 섹션에서 뉴스 링크를 수집하고 MongoDB에 저장합니다.

    Args:
        collection (MongoDB Collection): MongoDB 컬렉션 객체
    """
    # 기존에 저장된 뉴스 링크 가져오기
    link_dict = collection.find({}, {'_id': 0, 'news_link': 1})
    link_list = [i['news_link'] for i in link_dict]

    # Selenium 브라우저 설정 및 초기화
    chrome_options = selenium_setting()
    browser = init_browser(chrome_options)
    browser.get("https://news.naver.com/section/105")  # IT/과학 섹션으로 이동
    section_list = browser.find_elements(by=By.CSS_SELECTOR, value='#ct_wrap > div.ct_scroll_wrapper > div.column0 > div > ul > li > a')

    news_list = []  # 수집한 뉴스 데이터를 저장할 리스트

    # 각 섹션별 뉴스 데이터 수집
    for j in range(len(section_list)):
        section_list = browser.find_elements(by=By.CSS_SELECTOR, value='#ct_wrap > div.ct_scroll_wrapper > div.column0 > div > ul > li > a')
        section_link = section_list[j].get_attribute('href')
        browser.get(section_link)
        section_name = browser.find_element(by=By.CSS_SELECTOR, value='h3.section_title_h').text

        # '게임/리뷰' 섹션은 제외
        if section_name != '게임/리뷰':
            finish_check = False
            while True:
                # 뉴스 콘텐츠와 날짜 가져오기
                news_contents = browser.find_elements(by=By.CSS_SELECTOR, value='div.sa_text')
                news_date = news_contents[-1].find_elements(by=By.CSS_SELECTOR, value='div')[1].text.split('\n')[1]
                news_link = news_contents[-1].find_element(by=By.CSS_SELECTOR, value='a').get_attribute('href')

                # 특정 날짜 또는 중복된 링크가 있는 경우 종료
                if news_date in ['3일전', '4일전', '5일전', '6일전', '7일전'] or news_link in link_list:
                    break
                else:
                    # '더보기' 버튼 클릭
                    plus_btn = browser.find_elements(by=By.CSS_SELECTOR, value='#newsct > div.section_latest > div > div.section_more > a')
                    if finish_check:
                        break
                    elif len(plus_btn) != 0:
                        plus_btn[0].click()
                        time.sleep(1)

            # 수집한 뉴스 데이터 저장
            news_contents = browser.find_elements(by=By.CSS_SELECTOR, value='div.sa_text')
            for i in range(len(news_contents)):
                # 뉴스 제목, 내용, 회사, 날짜, 링크 수집
                news_title = news_contents[i].find_element(by=By.CSS_SELECTOR, value='a > strong').text
                news_content = news_contents[i].find_element(by=By.CSS_SELECTOR, value='div.sa_text_lede').text
                news_company = news_contents[i].find_element(by=By.CSS_SELECTOR, value='div.sa_text_info_left').text.split('\n')[0]
                news_date = news_contents[i].find_element(by=By.CSS_SELECTOR, value='div.sa_text_info_right').text
                news_link = news_contents[i].find_element(by=By.CSS_SELECTOR, value='a').get_attribute('href')

                # 3일 전 데이터까지만 수집
                if news_date == '3일전':
                    break
                elif news_link in link_list:
                    pass
                else:
                    # MongoDB에 저장
                    link_list.append(news_link)
                    dict_news = {
                        'news_title': news_title,
                        'news_part_content': news_content,
                        'news_company': news_company,
                        'news_date': news_date,
                        'news_link': news_link,
                        'section_type': section_name
                    }
                    collection.insert_one(dict_news)
                    news_list.append(dict_news)


def news_contents(collection, tokenizer, model):
    """
    수집된 뉴스 데이터를 상세히 크롤링하여 MongoDB에 저장합니다.

    Args:
        collection (MongoDB Collection): MongoDB 컬렉션 객체
        tokenizer (AutoTokenizer): NER 모델의 토크나이저
        model (AutoModelForTokenClassification): NER 모델
    """
    crawling_count = 0  # 크롤링된 뉴스 개수 초기화
    chrome_options = selenium_setting()
    news_list = collection.find({'noun_list': {'$exists': False}}, {'_id': 1, 'news_link': 1})
    browser = init_browser(chrome_options)

    for i in news_list:
        browser.get(i['news_link'])
        try:
            # 뉴스 날짜 추출
            news_date = browser.find_elements(by=By.CSS_SELECTOR, value='#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span')[-1].text
            news_date = news_date.replace('오후', 'PM').replace('오전', 'AM')
            news_date = pd.to_datetime(news_date, format='%Y.%m.%d. %p %I:%M')
        except:
            try:
                news_date = browser.find_elements(by=By.CSS_SELECTOR, value='#content > div.NewsEnd_container__HcfWh > div > div.NewsEnd_main_group__d5k8S > div > div.NewsEndMain_comp_article_head__Uqd6M > div.article_head_info > div.NewsEndMain_article_head_date_info__jGlzH > div> em')[-1].text
                news_date = news_date.replace('오후', 'PM').replace('오전', 'AM')
                news_date = pd.to_datetime(news_date, format='%Y.%m.%d. %p %I:%M')
            except:
                news_date = ''

        try:
            # 뉴스 본문 추출
            news_content_origin = browser.find_element(by=By.CSS_SELECTOR, value='#dic_area').text
        except:
            try:
                news_content_origin = browser.find_element(by=By.CSS_SELECTOR, value='#comp_news_article').text
            except:
                news_content_origin = ''

        # 본문에서 명사 추출
        noun_text = ner_remove_in_text(news_content_origin, model, tokenizer) if news_content_origin else ''

        # 기자 정보 추출
        try:
            news_journalist = browser.find_element(by=By.CSS_SELECTOR, value='div.media_end_head_journalist > a').text.replace(' 기자', '').split('\n')
        except:
            try:
                news_journalist = browser.find_element(by=By.CSS_SELECTOR, value='div.media_end_head_journalist > button').text.replace(' 기자', '').split('\n')
            except:
                try:
                    news_journalist = browser.find_element(by=By.CSS_SELECTOR, value='em.NewsEndMain_name__lNckc').text.replace(' 기자', '').split('\n')
                except:
                    news_journalist = []
        news_journalist = ', '.join(news_journalist)

        # MongoDB에 업데이트
        if noun_text:
            collection.update_one({'_id': i['_id']}, {'$set': {'news_date': news_date, 'news_journalist': news_journalist, 'noun_list': noun_text}})
        crawling_count += 1

    print('naver news crawling finish')
    print('crawling count : ', crawling_count)


def duplicated_data_delete(collection):
    """
    MongoDB에서 중복된 데이터를 삭제합니다.

    Args:
        collection (MongoDB Collection): MongoDB 컬렉션 객체
    """
    # 중복 데이터 탐지 및 삭제
    pipeline = [
        {
            "$group": {
                "_id": "$noun_list",  # noun_list 기준으로 그룹화
                "oldestId": {"$min": "$_id"},  # 가장 오래된 _id 찾기
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
    duplicates = list(collection.aggregate(pipeline))
    for doc in duplicates:
        if doc["idsToDelete"]:
            collection.delete_many({"_id": {"$in": doc["idsToDelete"]}})


def naver_news():
    """
    네이버 뉴스 데이터를 크롤링하여 MongoDB에 저장하고 중복 데이터를 제거합니다.
    """
    collection = mongo_setting('news_scraping', 'naver_news')
    tokenizer = AutoTokenizer.from_pretrained("KPF/KPF-bert-ner")
    model = AutoModelForTokenClassification.from_pretrained("KPF/KPF-bert-ner")
    link_list(collection)  # 뉴스 링크 수집
    news_contents(collection, tokenizer, model)  # 뉴스 상세 데이터 수집
    duplicated_data_delete(collection)  # 중복 데이터 삭제
