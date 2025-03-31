import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import gdown
import tempfile
import torch
from kobert_tokenizer import KoBERTTokenizer
from transformers import BertForSequenceClassification

# 환경변수에서 API 키 로드
load_dotenv()

# GPU 사용 여부 설정
# GPU가 사용 가능하면 "cuda", 그렇지 않으면 "cpu"를 사용
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model_from_drive(device):
    """
    Google Drive에서 학습된 모델을 다운로드하여 로드합니다.

    Args:
        device (torch.device): 모델을 로드할 장치 (GPU 또는 CPU).

    Returns:
        BertForSequenceClassification: 로드된 KoBERT 모델.
    """
    # 임시 파일 생성 (모델이 저장될 경로)
    with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as tmp_file:
        temp_model_path = tmp_file.name

        print("모델 다운로드 중...")
        # Google Drive에서 모델 다운로드
        classification_model = os.environ.get("classification_model")
        gdown.download(f"https://drive.google.com/uc?id={classification_model}", temp_model_path, quiet=False)

        # 클래스 리스트 정의
        class_list = [
            'IT_PC/기기', 'IT_게임', 'IT_과학', 'IT_모바일', 'IT_보안', 'IT_비즈니스/정책', 'IT_인터넷/SNS',
            'IT_콘텐츠', '건강/의료', '경제/산업', '과학/테크놀로지', '교육', '노동', '동물', '문화', '사건/사법', '스포츠',
            '오피니언/사설', '정치', '환경'
        ]

        # KoBERT 모델 초기화 및 가중치 로드
        model = BertForSequenceClassification.from_pretrained('skt/kobert-base-v1', num_labels=len(class_list))
        model.load_state_dict(torch.load(temp_model_path, map_location=device))

        # 임시 파일 삭제
        os.unlink(temp_model_path)

        return model.to(device)


def predict_single_text(text, model, tokenizer, device, max_len=128):
    """
    단일 텍스트를 입력받아 예측 결과를 반환합니다.

    Args:
        text(str): 입력 텍스트.
        model(BertForSequenceClassification): 학습된 KoBERT 모델.
        tokenizer(KoBERTTokenizer): KoBERT 토크나이저.
        device(torch.device): 모델이 실행되는 장치 (GPU 또는 CPU).
        max_len(int): 입력 텍스트의 최대 길이 (기본값: 128).

    Returns:
        preds(np.ndarray): 예측 확률 배열.
    """
    with torch.no_grad():
        # 입력 텍스트를 토크나이징 및 인코딩
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

        # 입력 데이터를 장치로 이동
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)

        # 모델 예측 수행
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        preds = torch.sigmoid(logits).cpu().numpy()

    return preds


def category_update(collection):
    """
    MongoDB 컬렉션의 문서에서 카테고리를 업데이트합니다.

    Args:
        collection (MongoDB Collection): MongoDB 컬렉션 객체.
    """
    # MongoDB에서 문서 가져오기
    documents = collection.find()
    df = pd.DataFrame(list(documents))

    # 카테고리가 비어 있는 문서 필터링
    df = df.loc[df['category'].isnull()]
    df = df.loc[~df['noun_list'].isnull()]

    print(f"Using device: {device}")

    # KoBERT 토크나이저 로드
    tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')

    # 클래스 리스트 정의
    class_list = [
        'IT_PC/기기', 'IT_게임', 'IT_과학', 'IT_모바일', 'IT_보안', 'IT_비즈니스/정책', 'IT_인터넷/SNS',
        'IT_콘텐츠', '건강/의료', '경제/산업', '과학/테크놀로지', '교육', '노동', '동물', '문화', '사건/사법', '스포츠',
        '오피니언/사설', '정치', '환경'
    ]

    # KoBERT 모델 로드
    model = load_model_from_drive(device)
    model.eval()

    # 각 문서에 대해 예측 수행 및 MongoDB 업데이트
    for index, row in df.iterrows():
        text = row['noun_list']
        predicted_label = predict_single_text(text, model, tokenizer, device)

        # 예측 확률이 0.5를 초과하는 클래스 인덱스 가져오기
        indices_above_threshold = np.where(predicted_label > 0.5)[1]
        predicted_classes = [class_list[i] for i in indices_above_threshold]

        # MongoDB 문서 업데이트
        collection.update_one(
            {'_id': row['_id']},  # 업데이트할 문서의 조건 (예: 고유 ID)
            {'$set': {'category': predicted_classes}}  # 업데이트할 필드
        )

    print("MongoDB collection updated successfully.")
