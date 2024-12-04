import re
import torch
from bson import ObjectId
from pymongo import MongoClient
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
from news_letter.ict_news import ict_news
from news_letter.seoul_institute import seoul_institute
from news_letter.statistic_bank import statistic_bank
from news_letter.venture_doctors import venture_doctors
from news_preprocess.category_classification import category_update
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from news_preprocess.keyword import keyword_update
import torch
from transformers import AutoModel, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity
from kss import split_sentences
import numpy as np
import networkx as nx
import zipfile
import gdown

# Google Drive에서 모델 다운로드 함수
def load_model_from_drive(device):
    # 임시 디렉토리 생성
    temp_dir = '/tmp/kobart_model'
    os.makedirs(temp_dir, exist_ok=True)

    # Google Drive에서 모델 압축 파일 다운로드
    print("모델 다운로드 중...")
    file_id = "1cX2XexdPsL5ygqtHJT4ZQhHKvOZq0skQ"  # 주어진 Google Drive 파일 ID
    zip_path = os.path.join(temp_dir, "kobart_model.zip")
    gdown.download(f"https://drive.google.com/uc?id={file_id}", zip_path, quiet=False)

    # 압축 해제
    print("모델 압축 해제 중...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 압축 파일 삭제
    os.remove(zip_path)
    print("모델 압축 해제 완료")

    # 모델 로드
    model_path = os.path.join(temp_dir, "kobart_summary_forth")  # 압축 해제된 폴더 경로
    model = BartForConditionalGeneration.from_pretrained(model_path)

    return model.to(device)
# 모델 및 토크나이저 로드

def embed_sentences(sentences, tokenizer, model):
    inputs = tokenizer(sentences, return_tensors='pt', padding=True, truncation=True, max_length=4096)
    with torch.no_grad():
        outputs = model(**inputs)
    # CLS 토큰의 임베딩을 사용
    return outputs.last_hidden_state[:, 0, :].numpy()

def extractive_summary(document, num_sentences=3):
    model_name = 'monologg/kobigbird-bert-base'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    sentence_embeddings = embed_sentences(document, tokenizer, model)

    # 문장 간 유사도 행렬 계산
    sim_matrix = cosine_similarity(sentence_embeddings)

    # 중요 문장 선택 (여기서는 가장 중앙에 위치한 문장 선택)
    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(nx_graph)

    # 중요 문장 선택
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(document)), reverse=True)
    if len(ranked_sentences) > num_sentences:
      summary_list = [ranked_sentences[i][1] for i in range(num_sentences)]
    else:
      summary_list = [ranked_sentences[i][1] for i in range(len(ranked_sentences))]

    summary = ' '.join(summary_list)
    return summary

def news_summary_extraction(document):
    document = document.split('\n')
    document_list = []
    for i in document:
      document_list.extend(split_sentences(i))
    summary = extractive_summary(document_list, num_sentences=3)
    return summary

def news_summary_abstraction(chunk,model):
    tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-base-v1')
    inputs = tokenizer(chunk, return_tensors='pt', max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs['input_ids'],
        max_length=150,
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3  # 3-gram 반복 방지
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def update_news_summary(collection):
    """
    MongoDB에 저장된 뉴스 데이터에 대해 요약을 수행하고 업데이트하는 함수.
    """
    # 요약되지 않은 뉴스 항목 가져오기

    news_data = collection.find({"abtraction": {"$exists": False}})
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    abtraction_model = load_model_from_drive(device)

    for news in news_data:
        news_id = news["_id"]
        content = news.get("news_content", "")
        if not content.strip():
            print(f"뉴스 {news_id}의 콘텐츠가 비어 있습니다.")
            continue
        try:
            extraction_summary = news_summary_extraction(content)
            abtraction_summary = news_summary_abstraction(extraction_summary,abtraction_model)

            # MongoDB 문서 업데이트
            collection.update_one({'_id': news_id}, {'$set': {'extraction': extraction_summary,'abtraction':abtraction_summary}})
        except Exception as e:
            print(f"Error occurred: {e}")

def total_update():
    load_dotenv()
    mongo_url = os.environ.get("DATABASE_URL")
    mongo_client = MongoClient(mongo_url)
    # database 연결
    database = mongo_client["news_scraping"]
    # collection 작업
    # ict_news()
    # seoul_institute()
    # statistic_bank()
    # venture_doctors()
    update_news_summary(database['news_list'])
    # category_update(database['news_list'])
    # keyword_update(database['news_list'])
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
