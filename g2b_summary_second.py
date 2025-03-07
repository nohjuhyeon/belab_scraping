from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from function_list.hwp_loader import HWPLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from konlpy.tag import Mecab
from kiwipiepy import Kiwi

kiwi = Kiwi()
# API 키 정보 로드
load_dotenv()
mecab = Mecab()
loader = HWPLoader('test.hwp')
documents = loader.load()
long_text = documents[0].page_content
# # 긴 문서 입력
# long_text = """
# 여기에 긴 텍스트를 입력하세요. TextRank는 문장 간 유사도를 기반으로 중요 문장을 선택하는 추출적 요약 알고리즘입니다.
# 문서를 그래프로 표현하고, 중요도를 계산하여 요약문을 생성합니다.
# """
# OpenAI 임베딩을 사용하여 의미론적 청크 분할기를 초기화합니다.
# text_splitter = SemanticChunker(OpenAIEmbeddings())
# chunks = text_splitter.split_text(long_text)

# # text_splitter를 사용하여 분할합니다.
# docs = text_splitter.create_documents([long_text])
# for i in docs:
#     print(i.page_content)  # 분할된 문서 중 첫 번째 문서의 내용을 출력합니다.
#     print('--------------------------------------------------------------')


text_splitter = SemanticChunker(
    # OpenAI의 임베딩 모델을 사용하여 시맨틱 청커를 초기화합니다.
    OpenAIEmbeddings(),
    # 분할 기준점 유형을 백분위수로 설정합니다.
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=70,
)

def apply_overlap(chunks, overlap_size):
    """
    청크 리스트에 오버랩을 추가하는 함수.
    
    :param chunks: 나뉜 텍스트 청크 리스트
    :param overlap_size: 오버랩 크기 (문자 수 기준)
    :return: 오버랩이 적용된 청크 리스트
    """
    overlapped_chunks = []
    for i in range(len(chunks)):
        if i == 0:
            # 첫 번째 청크는 그대로 추가
            overlapped_chunks.append(chunks[i])
        else:
            # 이전 청크의 끝부분과 현재 청크의 시작부분을 겹치게 함
            if overlap_size > len(chunks[i - 1].page_content.split('\n')):
                overlapped_text = '\n'.join(chunks[i - 1].page_content.split('\n')) + '\n' + chunks[i].page_content
                pass
            else:
                overlapped_text = '\n'.join(chunks[i - 1].page_content.split('\n')[-overlap_size:]) + '\n' + chunks[i].page_content
                pass
            overlapped_chunks.append(overlapped_text)
            chunks[i].page_content = overlapped_text
            pass
    return chunks

chunks = []

docs = text_splitter.create_documents([long_text])
for i, doc in enumerate(docs):
    # print(f"[Chunk {i}]", end="\n\n")
    # print(doc.page_content)  # 분할된 문서 중 첫 번째 문서의 내용을 출력합니다.
    chunks.append(doc.page_content)
    # print("===" * 20)

# 오버랩 적용
overlap_size = 2  # 오버랩 크기 (문자 수 기준)
overlapped_chunks = apply_overlap(docs, overlap_size)

for i, doc in enumerate(overlapped_chunks):
    print(f"[Chunk {i}]", end="\n\n")
    print(doc.page_content)  # 분할된 문서 중 첫 번째 문서의 내용을 출력합니다.
    # chunks.append(doc.page_contet)
    print("===" * 20)

embeddings = OpenAIEmbeddings()

def preprocess_text(text):
    tokens = [word.form for word in kiwi.analyze(text)[0][0]]  # 형태소만 추출
    return " ".join(tokens)
    # return " ".join(mecab.morphs(text))    

tokenizer_docs = [preprocess_text(text.page_content) for text in overlapped_chunks]

bm25_retriever  = BM25Retriever.from_texts(tokenizer_docs)
# db = FAISS.from_documents(overlapped_chunks, embeddings)


from langchain_core.runnables import ConfigurableField

# k 설정
# retriever = db.as_retriever(search_kwargs={"k": 1}).configurable_fields(
#     search_type=ConfigurableField(
#         id="search_type",
#         name="Search Type",
#         description="The search type to use",
#     ),
#     search_kwargs=ConfigurableField(
#         # 검색 매개변수의 고유 식별자를 설정
#         id="search_kwargs",
#         # 검색 매개변수의 이름을 설정
#         name="Search Kwargs",
#         # 검색 매개변수에 대한 설명을 작성
#         description="The search kwargs to use",
#     ),
# )

# retriever = db.as_retriever(
#     # 검색 유형을 "similarity_score_threshold 으로 설정
#     search_type="similarity_score_threshold",
#     # 임계값 설정
#     search_kwargs={"score_threshold": 0.7},
# )


# 검색 설정을 지정. Faiss 검색에서 k=3로 설정하여 가장 유사한 문서 3개를 반환
config = {"configurable": {"search_kwargs": {"k": 3}}}

# 관련 문서를 검색
docs = bm25_retriever.get_relevant_documents(preprocess_text("과업 수행 목적과 과업 수행에 대해 설명해줘"))

# 관련 문서를 검색
for doc in docs:
    print(overlapped_chunks[tokenizer_docs.index(doc.page_content)].page_content)
    print("=========================================================")