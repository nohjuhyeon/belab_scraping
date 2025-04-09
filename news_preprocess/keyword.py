from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from dotenv import load_dotenv
import os

# 환경변수에서 API 키 로드
loaded = load_dotenv(dotenv_path='/app/belab_scraping/.env')

def extract_keywords_frequency(text, num_keywords=5, stop_words=None):
    """
    주어진 텍스트에서 단어 빈도를 기반으로 상위 키워드를 추출합니다.

    Args:
        text(str): 입력 텍스트.
        num_keywords(int): 추출할 키워드 개수 (기본값: 5).
        stop_words(List[str]): 불용어 리스트.

    Returns:
        keyword_list(List[str]): 상위 키워드 리스트.
    """
    # CountVectorizer를 사용하여 단어 빈도 계산
    vectorizer = CountVectorizer(stop_words=stop_words, lowercase=False)

    # 텍스트를 리스트로 변환 (단일 문서도 리스트로 처리)
    documents = [text]

    try:
        # 단어 빈도 행렬 계산
        frequency_matrix = vectorizer.fit_transform(documents)

        # 단어 빈도와 단어 추출
        df = pd.DataFrame(frequency_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        # 빈도를 기준으로 상위 키워드 추출
        sorted_keywords = df.T.sort_values(by=0, ascending=False).head(num_keywords)
        keyword_list = sorted_keywords.index.tolist()
    except:
        # 예외 발생 시 빈 리스트 반환
        keyword_list = []

    return keyword_list


def keyword_update(collection):
    """
    MongoDB 컬렉션의 문서에서 키워드를 추출하여 업데이트합니다.

    Args:
        collection (MongoDB Collection): MongoDB 컬렉션 객체.
    """
    # MongoDB에서 문서 가져오기
    documents = collection.find()
    df = pd.DataFrame(list(documents))

    # 키워드가 비어 있고, 명사 리스트가 있는 문서 필터링
    df = df.loc[df['news_keywords'].isnull()]
    df = df.loc[~df['noun_list'].isnull()]

    # 불용어 파일 경로 설정
    folder_path = os.environ.get("folder_path")
    stop_word_file = folder_path + "news_preprocess/stop_word.txt"

    # 불용어 리스트 로드
    with open(stop_word_file, 'r', encoding='utf-8') as file:
        stop_words = file.read().splitlines()

    # 각 문서에 대해 키워드 추출 및 MongoDB 업데이트
    for index, row in df.iterrows():
        text = row['noun_list']
        keywords = extract_keywords_frequency(text, num_keywords=5, stop_words=stop_words)

        # MongoDB 문서 업데이트
        collection.update_one(
            {'_id': row['_id']},  # 업데이트할 문서의 조건 (예: 고유 ID)
            {'$set': {'news_keywords': keywords}}  # 업데이트할 필드
        )

    print("MongoDB collection updated successfully.")
