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

# 환경변수에서 API 키 읽기
load_dotenv()

API_KEY = os.environ.getenv('BAREUN_API_KEY')
# 공식 API 서버 사용
t = Tagger(API_KEY, "api.bareun.ai", 443)
# 또는 로컬 서버 사용
# t = Tagger(API_KEY, "bareun-server", 5656)

def clean_korean_documents(documents):
    #텍스트 정제 (특수기호 제거)
    documents = re.sub(r'[^ ㄱ-ㅣ가-힣]', '', documents) #특수기호 제거, 정규 표현식
    #텍스트 정제 (형태소 분석)
    clean_words = []
    # clean_words.extend(t.tags([document]).morphs())  # 결과 저장
    clean_words.extend(t.tags([documents]).nouns())  # 결과 저장
    documents = ' '.join(clean_words)
    return documents

text = '내고유명사로 존재하는 "크리스토퍼놀란"은 코로나19 상황 속에서도 걸어서세계속으로라는 TV 프로그램을 통해 바나나우유를 마시며 카톡하다가 떠오른 신박한 아이디어로 판타스틱한 로맨틱 영화를 만들 계획이며, 그 과정에서 디지털인문학의 도움을 받아 코로나백신에 대한 사회적 이슈도 함께 다루려 한다.'
summary = clean_korean_documents(text)
print(summary)