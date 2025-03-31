import torch
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration
from transformers import AutoModel, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity
from kss import split_sentences
import networkx as nx
import zipfile
import gdown
import os


def load_model_from_drive(device):
    """
    Google Drive에서 KoBART 모델을 다운로드하여 로드하는 함수.

    Args:
        device (torch.device): 모델을 로드할 디바이스(CPU 또는 GPU).

    Returns:
        BartForConditionalGeneration: 로드된 KoBART 모델.
    """
    # 임시 디렉토리 생성
    temp_dir = '/tmp/kobart_model'
    os.makedirs(temp_dir, exist_ok=True)

    # Google Drive에서 모델 압축 파일 다운로드
    print("모델 다운로드 중...")
    summary_model = os.environ.get("summary_model")
    zip_path = os.path.join(temp_dir, "kobart_model.zip")
    gdown.download(f"https://drive.google.com/uc?id={summary_model}", zip_path, quiet=False)

    # 압축 해제
    print("모델 압축 해제 중...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # 압축 파일 삭제
    os.remove(zip_path)
    print("모델 압축 해제 완료")

    # 모델 로드
    model_path = os.path.join(temp_dir, "kobart_summary_forth")
    model = BartForConditionalGeneration.from_pretrained(model_path)

    return model.to(device)


def embed_sentences(sentences, tokenizer, model):
    """
    입력 문장을 임베딩 벡터로 변환.

    Args:
        sentences (List[str]): 문장 리스트.
        tokenizer: 토크나이저.
        model: 임베딩 생성을 위한 모델.

    Returns:
        output_embedding(numpy.ndarray): 문장 임베딩 벡터.
    """
    inputs = tokenizer(sentences, return_tensors='pt', padding=True, truncation=True, max_length=4096)
    with torch.no_grad():
        outputs = model(**inputs)
    # CLS 토큰의 임베딩을 반환
    output_embedding = outputs.last_hidden_state[:, 0, :].numpy()
    return output_embedding


def extractive_summary(document, num_sentences=3):
    """
    입력 문서에서 추출적 요약을 생성.

    Args:
        document(List[str]): 문장 리스트.
        num_sentences (int): 요약에 포함할 문장 수.

    Returns:
        summary(str): 추출적 요약 결과.
    """
    model_name = 'monologg/kobigbird-bert-base'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    # 문장 임베딩 생성
    sentence_embeddings = embed_sentences(document, tokenizer, model)

    # 문장 간 유사도 행렬 계산
    sim_matrix = cosine_similarity(sentence_embeddings)

    # 중요 문장 선택 (PageRank 알고리즘 사용)
    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(nx_graph)

    # 문장 점수에 따라 정렬
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(document)), reverse=True)

    # 상위 문장 선택
    if len(ranked_sentences) > num_sentences:
        summary_list = [ranked_sentences[i][1] for i in range(num_sentences)]
    else:
        summary_list = [ranked_sentences[i][1] for i in range(len(ranked_sentences))]

    summary = ' '.join(summary_list)
    return summary


def news_summary_extraction(document):
    """
    뉴스 문서에서 추출적 요약 생성.

    Args:
        document (str): 뉴스 문서 텍스트.

    Returns:
        summary(str): 추출적 요약 결과.
    """
    document = document.split('\n')  # 문서를 줄 단위로 분리
    document_list = []
    for i in document:
        document_list.extend(split_sentences(i))  # 문장을 세부적으로 분리
    summary = extractive_summary(document_list, num_sentences=3)
    return summary


def news_summary_abstraction(chunk, model):
    """
    입력 텍스트에 대해 생성적 요약(추상적 요약)을 수행.

    Args:
        chunk (str): 입력 텍스트.
        model: KoBART 모델.

    Returns:
        summary(str): 생성적 요약 결과.
    """
    tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-base-v1')
    inputs = tokenizer(chunk, return_tensors='pt', max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs['input_ids'],
        max_length=150,
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3  # 3-gram 반복 방지
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def update_news_summary(collection):
    """
    MongoDB에 저장된 뉴스 데이터에 대해 요약을 수행하고 업데이트.

    Args:
        collection (MongoDB Collection): MongoDB 컬렉션 객체.
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
            # 추출적 요약 생성
            extraction_summary = news_summary_extraction(content)

            # 추상적 요약 생성
            abtraction_summary = news_summary_abstraction(extraction_summary, abtraction_model)

            # MongoDB 문서 업데이트
            collection.update_one(
                {'_id': news_id},
                {'$set': {'extraction': extraction_summary, 'abtraction': abtraction_summary}}
            )
        except Exception as e:
            print(f"Error occurred: {e}")
