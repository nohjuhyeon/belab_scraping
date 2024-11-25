from sklearn.datasets import load_files
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
import pickle
import re
import nltk
import numpy as np
import sys
from bareunpy import Tagger
import google.protobuf.text_format as tf
import os
from dotenv import load_dotenv

# 환경변수에서 API 키 읽기
load_dotenv()

# 또는 로컬 서버를 실행 중인 경우:
# t = Tagger(API_KEY, "localhost", 5757)
// ... existing code ...

import gdown
import os
import tempfile

def load_model_from_drive(device):
    with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as tmp_file:
        temp_model_path = tmp_file.name
        
        print("모델 다운로드 중...")
        file_id = "1-3lWWtppGyMgnAPwZDr13e-3m0LpRBUO"
        gdown.download(f"https://drive.google.com/uc?id={file_id}", temp_model_path, quiet=False)
        
        model = BertForSequenceClassification.from_pretrained('skt/kobert-base-v1', num_labels=len(class_list))
        model.load_state_dict(torch.load(temp_model_path, map_location=device))
        
        os.unlink(temp_model_path)
        
        return model.to(device)

# 기존 모델 로드 부분을 다음과 같이 변경



def clean_korean_documents(documents):
    API_KEY = os.environ.get('BAREUN_KEY')
    t = Tagger(API_KEY, "host.docker.internal", 5757)
    documents = re.sub(r'[^ ㄱ-ㅣ가-힣]', '', documents) #특수기호 제거, 정규 표현식
    clean_words = []
    clean_words.extend(t.tags([documents]).nouns())  # 결과 저장
    documents = ' '.join(clean_words)
    return documents



import torch
from kobert_tokenizer import KoBERTTokenizer
from transformers import BertForSequenceClassification
import numpy as np

# GPU 사용 설정


def predict_single_text(text, model, tokenizer, device, max_len=128):

    with torch.no_grad():
        encoding = tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        preds = torch.sigmoid(logits).cpu().numpy()

    return preds

from pymongo import MongoClient

def category_update(collection):
    documents = collection.find()
    df = pd.DataFrame(list(documents))
    df = df.loc[df['category'].isnull()]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # KoBERT 로드
    tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
    class_list = ['IT_PC/기기', 'IT_게임', 'IT_과학', 'IT_모바일', 'IT_보안', 'IT_비즈니스/정책',
        'IT_인터넷/SNS', 'IT_콘텐츠', '건강/의료', '경제', '경제/산업', '과학/테크놀로지', '교육',
        '국제', '날씨', '노동', '동물', '문화', '미디어', '사건/사법', '사회', '사회_일반', '스포츠',
        '여성', '오피니언/사설', '장애인', '정치', '환경']
    # 레이블의 수를 고유한 클래스 수로 설정 (이전 학습 시 사용한 것과 동일해야 함)
    num_labels = len(class_list)  # 예시로 5개로 설정, 실제 학습 시 사용한 클래스 수로 변경

    # 모델 로드
    model = BertForSequenceClassification.from_pretrained('skt/kobert-base-v1', num_labels=num_labels)
    classification_model_path = '/app/belab_scraping/news_preprocess/category_model.pt'
    model = load_model_from_drive(device)
    model.eval()
    for index, row in df.iterrows():
        text = row['news_content']
        text_to_predict = clean_korean_documents(text)
        predicted_label = predict_single_text(text_to_predict, model, tokenizer, device)

        indices_above_threshold = np.where(predicted_label > 0.5)[1]
        predicted_classes = [class_list[i] for i in indices_above_threshold]

        # MongoDB 문서 업데이트
        collection.update_one(
            {'_id': row['_id']},  # 업데이트할 문서의 조건 (예: 고유 ID)
            {'$set': {'category': predicted_classes}}  # 업데이트할 필드
        )

    print("MongoDB collection updated successfully.")
