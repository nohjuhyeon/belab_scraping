import re
import torch
from bson import ObjectId
from pymongo import MongoClient
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
from news_letter.ict_news import ict_news
from news_letter.seoul_institute import seoul_institute
from news_letter.statistic_bank import statistic_bank
from news_letter.venture_doctors import venture_doctors
import os
from dotenv import load_dotenv
import logging
from datetime import datetime


# KoBART 모델과 토크나이저 불러오기
tokenizer = PreTrainedTokenizerFast.from_pretrained("ainize/kobart-news")
model = BartForConditionalGeneration.from_pretrained("ainize/kobart-news")

def split_text(input_list, partition):
    """
    입력 텍스트 리스트를 파티션 단위로 분할합니다.
    """
    if partition == 1:
        return [' '.join(input_list)]
    
    size = len(input_list) // partition
    # 오버랩을 추가해 분리된 문맥이 더 자연스럽게 연결되도록 함
    return [
        ' '.join(input_list[max(0, i * size - 2):(i + 1) * size])
        for i in range(partition)
    ]

def summary(row):
    """
    뉴스 텍스트를 요약하는 함수.
    """
    try:
        paragraphs = row.split('\n')
        input_list = []

        # '다.'를 기준으로 문장 분리 후 리스트에 추가
        for paragraph in paragraphs:
            if '다.' in paragraph:
                sentences = re.findall(r'.*?다\.', paragraph)
                input_list.extend(sentences)

        # 텍스트 길이에 따라 파티션 분할
        partition = max(1, len(row) // 1800 + 1)
        input_list = split_text(input_list, partition)

        summary_first = ''
        for text in input_list:
            input_ids = tokenizer.encode(text, truncation=True, return_tensors='pt')
            summary_ids = model.generate(
                input_ids=input_ids,
                length_penalty=1.0,
                max_length=250,
                min_length=56,
                num_beams=4
            )
            summary_first += tokenizer.decode(summary_ids[0], skip_special_tokens=True) + ' '

        # 최종 요약 수행
        if len(input_list) > 1:
            input_ids = tokenizer.encode(summary_first.strip(), truncation=True, return_tensors='pt')
            final_summary_ids = model.generate(
                input_ids=input_ids,
                length_penalty=1.0,
                max_length=300,
                min_length=56,
                num_beams=4
            )
            full_summary = tokenizer.decode(final_summary_ids[0], skip_special_tokens=True)
        else:
            full_summary = summary_first.strip()

        return summary_first.strip(), full_summary
    except Exception as e:
        print(f"요약 중 오류 발생: {e}")
        return None, None

def update_news_summary(collection):
    """
    MongoDB에 저장된 뉴스 데이터에 대해 요약을 수행하고 업데이트하는 함수.
    """
    # 요약되지 않은 뉴스 항목 가져오기

    news_data = collection.find({"full_summary": {"$exists": False}})

    for news in news_data:
        news_id = news["_id"]
        content = news.get("news_content", "")

        if not content.strip():
            print(f"뉴스 {news_id}의 콘텐츠가 비어 있습니다.")
            continue

        # 뉴스 콘텐츠 요약
        first_summary, full_summary = summary(content)

        if full_summary:
            try:
                # MongoDB에 요약 업데이트
                collection.update_one(
                    {"_id": news_id},
                    {"$set": {"first_summary": first_summary, "full_summary": full_summary}}
                )
                print(f"뉴스 {news_id} 요약 완료")
            except Exception as e:
                print(f"뉴스 {news_id} 업데이트 중 오류 발생: {e}")

def total_update():
    load_dotenv()
    mongo_url = os.environ.get("DATABASE_URL")
    mongo_client = MongoClient(mongo_url)
    # database 연결
    database = mongo_client["news_scraping"]
    # collection 작업
    ict_news()
    update_news_summary(database['ict_news'])
    seoul_institute()
    update_news_summary(database['seoul_institute'])
    statistic_bank()
    update_news_summary(database['statistic_bank'])
    venture_doctors()
    update_news_summary(database['venture_doctors'])

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
