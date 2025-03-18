from dotenv import load_dotenv
import pandas as pd 
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from function_list.g2b_func_test_second import detect_file_type, notice_keyword_search
from llm_prompt_test.local_llm_summary import llm_summary
from llm_prompt_test.local_llm_cate_classification import llm_category_classification
import json
# MongoDB 연결 설정
load_dotenv()

file_path = 'test2.hwp'
text = detect_file_type(file_path)
text= text[:4000]
text_list = text.split('\n')[:-1]
context='\n'.join(text_list)

# notice_type = notice_keyword_search(context)
summary = llm_summary(context)
print(summary)
# summary ="해당 공고는 드론과 인공지능(AI)을 활용한 수질오염 감시 및 공간분석 용역을 위한 것으로, 옥정호 수계에 영향을 미치는 영양염류의 유입을 방지하기 위해 하천 주변 퇴비 보관 현황조사를 수행하고 부적정한 정보관 퇴비를 계도하는 것을 목적으로 합니다. 또한 드론 영상 데이터 구축과 AI 학습 데이터 구축을 통해 비점오염원을 자동으로 추출하고 3차원 모델 제작 및 공간분석을 수행하여 오염원과 인접 하천 간 최단 거리를 분석하고 수문 분석을 실시합니다."
category_dict = llm_category_classification(summary)
print(category_dict)
pass