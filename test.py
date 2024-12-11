# text = """
# 더불어민주당 이재명 대표가 이른바 '성남FC 후원금 의혹' 사건과 관련해 오는 10일 검찰에 출석해 조사를 받는다.

# 민주당 안호영 수석대변인은 6일 국회 브리핑을 통해 "이 대표가 10일 오전 10시 30분에 수원지검 성남지청에 출석하는 일정이 합의됐다"고 밝혔다.

# 안 수석대변인은 "검찰과 변호인단이 출석 날짜를 조율했고, 그 날짜가 적당하다고 판단한 것"이라고 설명했다.

# 공개적으로 출석하느냐는 질문에는 "이 대표는 당당히 출석해서 입장을 말씀하신다고 했다"며 "구체적으로 어떤 사람과 갈지, 어떻게 할지는 지켜봐야 한다"고 말했다.

# 앞서 검찰은 이 사건과 관련해 이 대표에게 지난해 12월 28일 소환을 통보했으나, 이 대표는 미리 잡아 둔 일정이 있다며 출석을 거부했다.

# 다만 이 대표는 "가능한 날짜와 조사 방식에 대해 변호인을 통해 협의해서 결정하겠다"며 조사에 응하겠다는 뜻을 밝혔고, 이후 검찰이 다시 요청한 10∼12일 중에서 출석 일자를 조율해 왔다.

# 성남FC 후원금 의혹 사건은 이 대표가 성남시장 재직 시절 성남FC 구단주로 있으면서 2016∼2018년 네이버·두산건설 등 기업들로부터 160억여원의 후원금을 유치하고, 이들 기업은 건축 인허가나 토지 용도 변경 등 편의를 받았다는 내용이다.

# 이 대표는 2018년 당시 바른미래당 등으로부터 이 의혹으로 고발당했다. 현재 제3자 뇌물공여 혐의를 받는 피의자 신분이다.

# 이 대표가 취임 이후 검찰의 소환조사에 응하는 것은 처음이다.

# 검찰은 앞서 지난 8월에도 대선 과정에서 허위 사실을 공표했다는 혐의로 이 대표에게 소환을 통보했으나, 당시 이 대표는 출석을 거부하고 서면 답변서만 제출한 바 있다.
# """
# from transformers import AutoTokenizer, BertForTokenClassification, logging, AutoModelForTokenClassification
# logging.set_verbosity_error()
# from konlpy.tag import Mecab
# import sys, os, torch
# import numpy as np
# import kss
# from news_preprocess import ner_label

# tokenizer = AutoTokenizer.from_pretrained("KPF/KPF-bert-ner")
# model = AutoModelForTokenClassification.from_pretrained("KPF/KPF-bert-ner")


# def remove_proper_nouns_from_text(text, ner_results):
#     """
#     고유 명사(Proper Nouns)의 위치를 기반으로 원문에서 해당 부분을 공백으로 처리.

#     Args:
#         text (str): 원문 텍스트
#         ner_results (list): ner_predict 함수에서 반환된 고유 명사 리스트 (word, start, end 포함)

#     Returns:
#         str: 고유 명사가 제거된 텍스트
#     """
#     text_chars = list(text)  # 문자열을 문자 리스트로 변환 (수정 가능하도록)
#     for ner in ner_results:
#         start, end = ner["start"], ner["end"]
#         # 고유 명사 위치를 공백으로 대체
#         for i in range(start, end):
#             text_chars[i] = " "  # 해당 위치를 공백으로 설정

#     # 문자 리스트를 다시 문자열로 변환
#     return ''.join(text_chars)

# def ner_predict(sent):
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model.to(device)
#     sent_list = []
#     sent = sent.replace(" ", "-")  # 공백을 하이픈으로 대체
#     test_tokenized = tokenizer(sent, return_tensors="pt")

#     inputs = {
#         "input_ids": test_tokenized["input_ids"].to(device),
#         "attention_mask": test_tokenized["attention_mask"].to(device),
#         "token_type_ids": test_tokenized["token_type_ids"].to(device)
#     }

#     # 모델 예측
#     outputs = model(**inputs)
#     token_predictions = outputs[0].argmax(dim=2)
#     token_prediction_list = token_predictions.squeeze(0).tolist()

#     # 레이블 매핑
#     pred_str = [ner_label.id2label[l] for l in token_prediction_list]
#     token_offsets = tokenizer(sent).encodings[0].offsets  # 토큰 오프셋

#     # 고유 명사 추출
#     is_prev_entity = False
#     prev_entity_tag = ""
#     _word = ""
#     start_pos = -1
#     end_pos = -1

#     for i, (offset, pred) in enumerate(zip(token_offsets, pred_str)):
#         if i == 0 or i == len(pred_str) - 1:
#             continue  # CLS/SEP 토큰 제외

#         if 'B-' in pred:
#             if is_prev_entity:
#                 sent_list.append({
#                     "word": _word.strip(),
#                     "label": prev_entity_tag,
#                     "start": start_pos,
#                     "end": end_pos
#                 })
#             _word = sent[offset[0]:offset[1]]
#             start_pos, end_pos = offset
#             prev_entity_tag = pred[2:]
#             is_prev_entity = True
#         elif 'I-' in pred and is_prev_entity:
#             _word += sent[offset[0]:offset[1]]
#             end_pos = offset[1]
#         else:
#             if is_prev_entity:
#                 sent_list.append({
#                     "word": _word.strip(),
#                     "label": prev_entity_tag,
#                     "start": start_pos,
#                     "end": end_pos
#                 })
#             is_prev_entity = False
#             _word = ""
#     return sent_list

# def extract_nng_sl_with_positions(text):
#     """
#     Mecab을 사용하여 NNG(일반 명사)와 SL(외국어) 품사를 추출하고, 해당 단어의 위치를 반환.

#     Args:
#         text (str): Mecab으로 처리할 텍스트

#     Returns:
#         list: NNG, SL 품사에 해당하는 단어와 위치 정보 (word, start, end 포함)
#     """
#     mecab = Mecab()
#     pos_tags = mecab.pos(text)  # Mecab으로 품사 태깅
#     nng_sl_results = []

#     start_idx = 0
#     for word, pos in pos_tags:
#         if pos in ['NNG', 'SL']:  # NNG(일반 명사)와 SL(외국어)만 추출
#             # 단어의 시작 위치와 끝 위치 계산
#             start_idx = text.find(word, start_idx)  # 현재 위치 이후에서 단어를 찾음
#             if start_idx != -1:
#                 end_idx = start_idx + len(word)
#                 nng_sl_results.append({'word': word, 'start': start_idx, 'end': end_idx})
#                 start_idx = end_idx  # 다음 검색을 위해 위치 갱신

#     return nng_sl_results


# def ner_remove_in_text(text):
#   text = text.replace('\n', '')  # 텍스트 전처리
#   sents = kss.split_sentences(text)  # 문장 단위로 분리
#   text_list=[]
#   modified_text_list = []
#   noun_list = []
#   for i in sents:
#     text_dict = ner_predict(i)
#     del_label_list = ['CV_POSITION','DT_DURATION','DT_DAY','DT_WEEK','DT_MONTH','DT_YEAR','DT_SEASON','DT_GEOAGE','DT_DYNASTY','DT_OTHERS','TI_DURATION','TI_HOUR','TI_MINUTE','TI_SECOND','TI_OTHERS','QT_AGE','QT_SIZE','QT_LENGTH','QT_COUNT','QT_MAN_COUNT','QT_WEIGHT','QT_PERCENTAGE','QT_SPEED','QT_TEMPERATURE','QT_VOLUME','QT_ORDER','QT_PRICE','QT_PHONE','QT_SPORTS','QT_CHANNEL','QT_ALBUM','QT_ADDRESS','QT_OTHERS','TMI_SITE','TMI_EMAIL','TMI_MODEL']
#     sent_list = []
#     for j in text_dict:
#       word_list = []
#       if j['label'] not in del_label_list:
#         word_list.append(j)
#       sent_list.extend(word_list)
#     text_list.append(sent_list)

#     text_without_proper_nouns = remove_proper_nouns_from_text(i, sent_list)
#     nng_sl_results = extract_nng_sl_with_positions(text_without_proper_nouns)
#     sent_list.extend(nng_sl_results)
#     sent_list = sorted(sent_list, key=lambda x: x['start'])
#     noun_list.append(' '.join([i['word'] for i in sent_list]))
#     modified_text_list.append(text_without_proper_nouns)
#   return  ' '.join(noun_list)

# noun_text = ner_remove_in_text(text)
# print(noun_text)

from konlpy.tag import Mecab

mecab = Mecab()

word_list = ['QR코드', '플랫폼','오버프로비저닝','딥페이크',]

for word in word_list:
  print(mecab.pos(word))