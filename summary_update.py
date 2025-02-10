from pymongo import MongoClient
from news_letter.naver_new import naver_news
from news_preprocess.summarization import update_news_summary
from news_preprocess.category_classification import category_update
from news_preprocess.noun_extraction import noun_extraction
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from news_preprocess.keyword import keyword_update
import torch



def total_update():
    load_dotenv()
    mongo_url = os.environ.get("DATABASE_URL")
    mongo_client = MongoClient(mongo_url)
    # database 연결
    database = mongo_client["news_scraping"]
    # collection 작업
    # seoul_institute()
    # naver_news()
    noun_extraction(database['naver_news'])
    # update_news_summary(database['naver_news'])
    # category_update(database['naver_news'])
    # keyword_update(database['naver_news'])
    # update_news_summary(database['report_list'])
    # keyword_update(database['report_list'])

try:
    print("----------------뉴스 요약 업데이트 시작----------------")
    print(datetime.now())
    load_dotenv()
    folder_path = os.environ.get("folder_path")
    logging.basicConfig(filename=folder_path+'/log_list/scheduler.txt', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("----------------news summarization started----------------") # 스케줄러 시작 로그 기록
    total_update()

except (KeyboardInterrupt, SystemExit):
    print("summarization shut down.")
    logging.info("summarization shut down.") # 스케줄러 종료 로그 기록
finally:
    print("뉴스 요약 업데이트 완료!")
