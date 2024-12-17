import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

# 환경변수에서 API 키 읽기
load_dotenv()


import gdown
import os
import tempfile

def load_model_from_drive(device):
    with tempfile.NamedTemporaryFile(suffix='.pt', delete=False) as tmp_file:
        temp_model_path = tmp_file.name
        
        print("모델 다운로드 중...")
        file_id = "1pGK7NuociQRSv9MLL-pUkrcR43eCxj7L"
        gdown.download(f"https://drive.google.com/uc?id={file_id}", temp_model_path, quiet=False)
        class_list = ['IT_PC/기기','IT_게임','IT_과학','IT_모바일','IT_보안','IT_비즈니스/정책','IT_인터넷/SNS',
        'IT_콘텐츠','건강/의료', '경제/산업','과학/테크놀로지','교육','노동','동물','문화','사건/사법','스포츠',
        '오피니언/사설','정치','환경']
        model = BertForSequenceClassification.from_pretrained('skt/kobert-base-v1', num_labels=len(class_list))
        model.load_state_dict(torch.load(temp_model_path, map_location=device))
        
        os.unlink(temp_model_path)
        
        return model.to(device)

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


def category_update(collection):
    documents = collection.find()
    df = pd.DataFrame(list(documents))
    df = df.loc[df['category'].isnull()]
    df = df.loc[~df['noun_list'].isnull()]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # KoBERT 로드
    tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')
    class_list = ['IT_PC/기기','IT_게임','IT_과학','IT_모바일','IT_보안','IT_비즈니스/정책','IT_인터넷/SNS',
    'IT_콘텐츠','건강/의료', '경제/산업','과학/테크놀로지','교육','노동','동물','문화','사건/사법','스포츠',
    '오피니언/사설','정치','환경']
    # 레이블의 수를 고유한 클래스 수로 설정 (이전 학습 시 사용한 것과 동일해야 함)
    num_labels = len(class_list)  # 예시로 5개로 설정, 실제 학습 시 사용한 클래스 수로 변경

    # 모델 로드
    model = load_model_from_drive(device)
    model.eval()
    for index, row in df.iterrows():
        text = row['noun_list']
        predicted_label = predict_single_text(text, model, tokenizer, device)

        indices_above_threshold = np.where(predicted_label > 0.5)[1]
        predicted_classes = [class_list[i] for i in indices_above_threshold]

        # MongoDB 문서 업데이트
        collection.update_one(
            {'_id': row['_id']},  # 업데이트할 문서의 조건 (예: 고유 ID)
            {'$set': {'category': predicted_classes}}  # 업데이트할 필드
        )

    print("MongoDB collection updated successfully.")
