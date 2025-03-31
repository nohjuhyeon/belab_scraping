from transformers import AutoTokenizer, logging, AutoModelForTokenClassification
logging.set_verbosity_error()  # Transformer 라이브러리의 경고 메시지 비활성화
from konlpy.tag import Mecab
import os, torch
import kss
from news_preprocess import ner_label
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
import time

def remove_proper_nouns_from_text(text, ner_results):
    """
    고유 명사(Proper Nouns)의 위치를 기반으로 원문에서 해당 부분을 공백으로 처리.

    Args:
        text (str): 원문 텍스트.
        ner_results (list): ner_predict 함수에서 반환된 고유 명사 리스트 (word, start, end 포함).

    Returns:
        modified_text (str): 고유 명사가 제거된 텍스트.
    """
    text_chars = list(text)  # 문자열을 수정 가능한 문자 리스트로 변환
    for ner in ner_results:
        start, end = ner["start"], ner["end"]
        # 고유 명사 위치를 공백으로 대체
        for i in range(start, end):
            text_chars[i] = " "
    modified_text = ''.join(text_chars)  # 문자 리스트를 다시 문자열로 변환
    return modified_text


def ner_predict(sent, model, tokenizer):
    """
    입력 문장에서 NER(Named Entity Recognition)을 수행하여 고유 명사를 추출.

    Args:
        sent (str): 입력 문장.
        model: 미리 학습된 NER 모델.
        tokenizer: NER 모델에 사용할 토크나이저.

    Returns:
        sent_list(List[dict]): 고유 명사와 해당 위치 정보를 포함한 리스트.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # 입력 문장의 공백을 하이픈으로 대체
    sent = sent.replace(" ", "-")
    test_tokenized = tokenizer(sent, return_tensors="pt")

    # 입력 데이터 생성
    inputs = {
        "input_ids": test_tokenized["input_ids"].to(device),
        "attention_mask": test_tokenized["attention_mask"].to(device),
        "token_type_ids": test_tokenized["token_type_ids"].to(device)
    }

    # 모델 예측
    outputs = model(**inputs)
    token_predictions = outputs[0].argmax(dim=2)
    token_prediction_list = token_predictions.squeeze(0).tolist()

    # 레이블 매핑
    pred_str = [ner_label.id2label[l] for l in token_prediction_list]
    token_offsets = tokenizer(sent).encodings[0].offsets  # 토큰 오프셋

    # 고유 명사 추출
    sent_list = []
    is_prev_entity = False
    prev_entity_tag = ""
    _word = ""
    start_pos = -1
    end_pos = -1

    for i, (offset, pred) in enumerate(zip(token_offsets, pred_str)):
        if i == 0 or i == len(pred_str) - 1:  # CLS/SEP 토큰 제외
            continue

        if 'B-' in pred:  # 새로운 엔터티 시작
            if is_prev_entity:
                sent_list.append({
                    "word": _word.strip(),
                    "label": prev_entity_tag,
                    "start": start_pos,
                    "end": end_pos
                })
            _word = sent[offset[0]:offset[1]]
            start_pos, end_pos = offset
            prev_entity_tag = pred[2:]
            is_prev_entity = True
        elif 'I-' in pred and is_prev_entity:  # 기존 엔터티 연속
            _word += sent[offset[0]:offset[1]]
            end_pos = offset[1]
        else:  # 엔터티 종료
            if is_prev_entity:
                sent_list.append({
                    "word": _word.strip(),
                    "label": prev_entity_tag,
                    "start": start_pos,
                    "end": end_pos
                })
            is_prev_entity = False
            _word = ""

    return sent_list


def extract_nng_sl_with_positions(text):
    """
    Mecab을 사용하여 NNG(일반 명사)와 SL(외국어) 품사를 추출하고, 해당 단어의 위치를 반환.

    Args:
        text (str): Mecab으로 처리할 텍스트.

    Returns:
        nng_sl_results(List[dict]): NNG, SL 품사에 해당하는 단어와 위치 정보 (word, start, end 포함).
    """
    mecab = Mecab()
    pos_tags = mecab.pos(text)  # Mecab으로 품사 태깅
    nng_sl_results = []

    start_idx = 0
    for word, pos in pos_tags:
        if pos in ['NNG', 'SL']:  # NNG(일반 명사)와 SL(외국어)만 추출
            start_idx = text.find(word, start_idx)  # 단어의 시작 위치 찾기
            if start_idx != -1:
                end_idx = start_idx + len(word)
                nng_sl_results.append({'word': word, 'start': start_idx, 'end': end_idx})
                start_idx = end_idx  # 다음 검색을 위해 위치 갱신

    return nng_sl_results


def ner_remove_in_text(text, model, tokenizer):
    """
    텍스트에서 고유 명사를 제거하고 일반 명사와 외국어를 추출.

    Args:
        text (str): 입력 텍스트.
        model: 미리 학습된 NER 모델.
        tokenizer: NER 모델에 사용할 토크나이저.

    Returns:
        modified_text(str): 처리된 명사 리스트를 공백으로 연결한 문자열.
    """
    text = text.split('\n')  # 텍스트를 줄 단위로 분리
    sents = []
    for i in text:
        sents.extend(kss.split_sentences(i))  # 문장 단위로 분리

    text_list = []
    noun_list = []

    for i in sents:
        text_dict = []
        sent_list = []

        if len(i) <= 512:  # 문장 길이가 512 이하인 경우 처리
            text_dict = ner_predict(i, model, tokenizer)
            
            # 특정 레이블 제거
            del_label_list = [...]  # 제거할 레이블 리스트 (생략)
            for j in text_dict:
                if j['label'] not in del_label_list:
                    sent_list.append(j)

        # 고유 명사를 제거한 텍스트 생성
        text_without_proper_nouns = remove_proper_nouns_from_text(i, text_dict)
        nng_sl_results = extract_nng_sl_with_positions(text_without_proper_nouns)
        sent_list.extend(nng_sl_results)
        sent_list = sorted(sent_list, key=lambda x: x['start'])  # 위치 기준 정렬
        noun_list.append(' '.join([i['word'] for i in sent_list]))
        modified_text = ' '.join(noun_list)
    return modified_text

def noun_extraction(collection):
    """
    MongoDB 컬렉션의 문서에서 명사를 추출하여 업데이트.

    Args:
        collection (MongoDB Collection): MongoDB 컬렉션 객체.
    """
    load_dotenv()
    documents = collection.find()
    df = pd.DataFrame(list(documents))

    tokenizer = AutoTokenizer.from_pretrained("KPF/KPF-bert-ner")
    model = AutoModelForTokenClassification.from_pretrained("KPF/KPF-bert-ner")

    start_time = time.time()

    for index, row in df.iterrows():
        text = row['news_content']
        text = text.replace('\n', ' ').replace("과기정통부", "과학기술정보통신부").replace('AWS', '아마존웹서비스')

        noun_text = ner_remove_in_text(text, model, tokenizer)

        if noun_text != '':
            # MongoDB 문서 업데이트
            collection.update_one(
                {'_id': row['_id']},
                {'$set': {'noun_list': noun_text}}
            )

        if index % 100 == 0:  # 진행 상황 출력
            elapsed_time = time.time() - start_time
            elapsed_time_formatted = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            print(f"Index: {index}, Elapsed Time: {elapsed_time_formatted}")

    print("MongoDB collection updated successfully.")


if __name__ == "__main__":
    mecab = Mecab()

    # 테스트 단어 리스트
    word_list = ['QR코드', '플랫폼', '오버프로비저닝', '딥페이크', '머신러닝', '딥러닝', 'AI', 'GPT', 'LLM', '챗봇']

    for word in word_list:
        print(mecab.pos(word))

    mongo_url = os.environ.get("DATABASE_URL")
    mongo_client = MongoClient(mongo_url)

    # database 연결
    database = mongo_client["news_scraping"]

    # collection 작업
    collection = database['news_list']

    noun_extraction(collection)
