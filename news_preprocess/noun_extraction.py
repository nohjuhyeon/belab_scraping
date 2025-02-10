from transformers import AutoTokenizer, logging, AutoModelForTokenClassification
logging.set_verbosity_error()
from konlpy.tag import Mecab
import os, torch
import kss
from news_preprocess import ner_label
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import time
from konlpy.tag import Mecab


def remove_proper_nouns_from_text(text, ner_results):
    """
    고유 명사(Proper Nouns)의 위치를 기반으로 원문에서 해당 부분을 공백으로 처리.

    Args:
        text (str): 원문 텍스트
        ner_results (list): ner_predict 함수에서 반환된 고유 명사 리스트 (word, start, end 포함)

    Returns:
        str: 고유 명사가 제거된 텍스트
    """
    text_chars = list(text)  # 문자열을 문자 리스트로 변환 (수정 가능하도록)
    for ner in ner_results:
        start, end = ner["start"], ner["end"]
        # 고유 명사 위치를 공백으로 대체
        for i in range(start, end):
            text_chars[i] = " "  # 해당 위치를 공백으로 설정

    # 문자 리스트를 다시 문자열로 변환
    return ''.join(text_chars)

def ner_predict(sent,model,tokenizer):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    sent_list = []
    sent = sent.replace(" ", "-")  # 공백을 하이픈으로 대체
    test_tokenized = tokenizer(sent, return_tensors="pt")

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
    is_prev_entity = False
    prev_entity_tag = ""
    _word = ""
    start_pos = -1
    end_pos = -1

    for i, (offset, pred) in enumerate(zip(token_offsets, pred_str)):
        if i == 0 or i == len(pred_str) - 1:
            continue  # CLS/SEP 토큰 제외

        if 'B-' in pred:
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
        elif 'I-' in pred and is_prev_entity:
            _word += sent[offset[0]:offset[1]]
            end_pos = offset[1]
        else:
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
        text (str): Mecab으로 처리할 텍스트

    Returns:
        list: NNG, SL 품사에 해당하는 단어와 위치 정보 (word, start, end 포함)
    """
    mecab = Mecab()
    pos_tags = mecab.pos(text)  # Mecab으로 품사 태깅
    nng_sl_results = []

    start_idx = 0
    for word, pos in pos_tags:
        if pos in ['NNG', 'SL']:  # NNG(일반 명사)와 SL(외국어)만 추출
            # 단어의 시작 위치와 끝 위치 계산
            start_idx = text.find(word, start_idx)  # 현재 위치 이후에서 단어를 찾음
            if start_idx != -1:
                end_idx = start_idx + len(word)
                nng_sl_results.append({'word': word, 'start': start_idx, 'end': end_idx})
                start_idx = end_idx  # 다음 검색을 위해 위치 갱신

    return nng_sl_results


def ner_remove_in_text(text,model,tokenizer):
  text = text.split('\n')  # 텍스트 전처리
  sents = []
  for i in text:
    sents.extend(kss.split_sentences(i))  # 문장 단위로 분리
  text_list=[]
  noun_list = []
  for i in sents:
    text_dict = []
    sent_list = []
    if len(i) <= 512:
      text_dict = ner_predict(i,model,tokenizer)
      del_label_list = ['CV_POSITION','DT_DURATION','DT_DAY','DT_WEEK','DT_MONTH','DT_YEAR','DT_SEASON','DT_GEOAGE','DT_DYNASTY','DT_OTHERS','TI_DURATION','TI_HOUR','TI_MINUTE','TI_SECOND','TI_OTHERS','QT_AGE','QT_SIZE','QT_LENGTH','QT_COUNT','QT_MAN_COUNT','QT_WEIGHT','QT_PERCENTAGE','QT_SPEED','QT_TEMPERATURE','QT_VOLUME','QT_ORDER','QT_PRICE','QT_PHONE','QT_SPORTS','QT_CHANNEL','QT_ALBUM','QT_ADDRESS','QT_OTHERS','TMI_SITE','TMI_EMAIL','TMI_MODEL']
      for j in text_dict:
        word_list = []
        if j['label'] not in del_label_list:
          word_list.append(j)
        sent_list.extend(word_list)
    text_list.append(sent_list)

    text_without_proper_nouns = remove_proper_nouns_from_text(i, text_dict)
    nng_sl_results = extract_nng_sl_with_positions(text_without_proper_nouns)
    sent_list.extend(nng_sl_results)
    sent_list = sorted(sent_list, key=lambda x: x['start'])
    noun_list.append(' '.join([i['word'] for i in sent_list]))
  return  ' '.join(noun_list)









# Google Drive에서 모델 다운로드 함수    
def noun_extraction(collection):
  load_dotenv()
  documents = collection.find()
  df = pd.DataFrame(list(documents))
#   df = df.loc[df['noun_list'].isnull()]
  tokenizer = AutoTokenizer.from_pretrained("KPF/KPF-bert-ner")
  model = AutoModelForTokenClassification.from_pretrained("KPF/KPF-bert-ner")
  start_time = time.time()
  for index, row in df.iterrows():
      text = row['news_content']
      text = text.replace('\n',' ').replace("과기정통부", "과학기술정보통신부").replace('AWS','아마존웹서비스')
      noun_text = ner_remove_in_text(text,model,tokenizer)
      if noun_text != '':
        # MongoDB 문서 업데이트
        collection.update_one(
            {'_id': row['_id']},  # 업데이트할 문서의 조건 (예: 고유 ID)
            {'$set': {'noun_list': noun_text}}  # 업데이트할 필드
        )
      if index%100 == 0:
        elapsed_time = time.time() - start_time
        elapsed_time_formatted = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"Index: {index}, Elapsed Time: {elapsed_time_formatted}")
  print("MongoDB collection updated successfully.")
  
if __name__ == "__main__":
    mecab = Mecab()

    word_list = ['QR코드', '플랫폼','오버프로비저닝','딥페이크','머신러닝','딥러닝','AI','GPT','LLM','챗봇']

    for word in word_list:
        print(mecab.pos(word))  
    mongo_url = os.environ.get("DATABASE_URL")
    mongo_client = MongoClient(mongo_url)
    # database 연결
    database = mongo_client["news_scraping"]
    # collection 작업
    collection = database['news_list']

    noun_extraction(collection)

