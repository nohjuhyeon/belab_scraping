from pymongo import MongoClient
from dotenv import load_dotenv
import os 
# MongoDB 연결 설정
load_dotenv()
mongo_url = os.environ.get("DATABASE_URL")
mongo_client = MongoClient(mongo_url)
database = mongo_client["news_scraping"]
# collection 작업
# seoul_institute()
# naver_news()


print("중복 데이터 삭제 완료!")
