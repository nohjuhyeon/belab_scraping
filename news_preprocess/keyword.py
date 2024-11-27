from pymongo import MongoClient

from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
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
import bareunpy as brn
import google.protobuf.text_format as tf
from dotenv import load_dotenv
import os
from bareunpy import Tagger

# 환경변수에서 API 키 읽기
load_dotenv()

# 또는 로컬 서버를 실행 중인 경우:
# t = Tagger(API_KEY, "localhost", 5757)

def clean_korean_documents(documents):
    #텍스트 정제 (특수기호 제거)
    documents = re.sub(r'[^ ㄱ-ㅣ가-힣]', '', documents) #특수기호 제거, 정규 표현식
    #텍스트 정제 (형태소 분석)
    clean_words = []
    for i in t.tags([documents]).pos():
      if i[1] in ['NNG','NNP']:
        if i[1] == '비트코':
          clean_words.append('비트코인')
        else:
          clean_words.append(i[0])
    documents = ' '.join(clean_words)
    return documents


def load_stop_words(file_path):
    """파일에서 불용어를 읽어 리스트로 반환합니다."""
    with open(file_path, 'r', encoding='utf-8') as file:
        stop_words = file.read().splitlines()
    return stop_words

def extract_keywords_frequency(text, num_keywords=5, stop_words=None):
    # Count 벡터라이저 생성
    vectorizer = CountVectorizer(stop_words=stop_words)

    # 텍스트를 리스트로 변환 (단일 문서도 리스트로)
    documents = [text]

    # 단어 빈도 행렬 계산
    frequency_matrix = vectorizer.fit_transform(documents)

    # 단어 빈도와 단어 추출
    df = pd.DataFrame(frequency_matrix.toarray(), columns=vectorizer.get_feature_names_out())

    # 빈도를 기준으로 상위 키워드 추출
    sorted_keywords = df.T.sort_values(by=0, ascending=False).head(num_keywords)

    return sorted_keywords.index.tolist()



def keyword_update(collection):
  documents = collection.find()
  df = pd.DataFrame(list(documents))
  df = df.loc[df['news_keywords'].isnull()]
  stop_word_file = '/app/belab_scraping/news_preprocess/stop_word.txt'

  # 불용어 리스트 로드
  stop_words = load_stop_words(stop_word_file)
  for index, row in df.iterrows():
      text = row['news_content']
      text_to_predict = clean_korean_documents(text)
      if text_to_predict != '':
        keywords = extract_keywords_frequency(text_to_predict, num_keywords=5, stop_words=stop_words)

        # MongoDB 문서 업데이트
        collection.update_one(
            {'_id': row['_id']},  # 업데이트할 문서의 조건 (예: 고유 ID)
            {'$set': {'news_keywords': keywords}}  # 업데이트할 필드
        )

  print("MongoDB collection updated successfully.")

# 불용어 파일 경로

