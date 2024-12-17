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
import google.protobuf.text_format as tf
from dotenv import load_dotenv
import os

# 환경변수에서 API 키 읽기
load_dotenv()

# 또는 로컬 서버를 실행 중인 경우:
# t = Tagger(API_KEY, "localhost", 5757)


def load_stop_words(file_path):
    """파일에서 불용어를 읽어 리스트로 반환합니다."""
    with open(file_path, 'r', encoding='utf-8') as file:
        stop_words = file.read().splitlines()
    return stop_words

def extract_keywords_frequency(text, num_keywords=5, stop_words=None):
    # Count 벡터라이저 생성
    vectorizer = CountVectorizer(stop_words=stop_words, lowercase=False)

    # 텍스트를 리스트로 변환 (단일 문서도 리스트로)
    documents = [text]

    # 단어 빈도 행렬 계산
    try:
      frequency_matrix = vectorizer.fit_transform(documents)

      # 단어 빈도와 단어 추출
      df = pd.DataFrame(frequency_matrix.toarray(), columns=vectorizer.get_feature_names_out())

      # 빈도를 기준으로 상위 키워드 추출
      sorted_keywords = df.T.sort_values(by=0, ascending=False).head(num_keywords)
      keyword_list = sorted_keywords.index.tolist()
    except:
       keyword_list = []
    return keyword_list



def keyword_update(collection):
  documents = collection.find()
  df = pd.DataFrame(list(documents))
  df = df.loc[df['news_keywords'].isnull()]
  df = df.loc[~df['noun_list'].isnull()]

  stop_word_file = '/app/belab_scraping/news_preprocess/stop_word.txt'
  # 불용어 리스트 로드
  stop_words = load_stop_words(stop_word_file)
  for index, row in df.iterrows():
      text = row['noun_list']
      keywords = extract_keywords_frequency(text, num_keywords=5, stop_words=stop_words)

      # MongoDB 문서 업데이트
      collection.update_one(
          {'_id': row['_id']},  # 업데이트할 문서의 조건 (예: 고유 ID)
          {'$set': {'news_keywords': keywords}}  # 업데이트할 필드
      )

  print("MongoDB collection updated successfully.")

# 불용어 파일 경로

