from dotenv import load_dotenv
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from function_list.g2b_func_test_second import (
    detect_file_type,
    notice_keyword_search,
    llm_category_classification,
    llm_summary,
)
import json

# MongoDB 연결 설정
load_dotenv()

# file_path = 'test.hwpx'
# text = detect_file_type(file_path)
# text= text[:4000]
# text_list = text.split('\n')[:-1]
# context='\n'.join(text_list)

# notice_type = notice_keyword_search(context)
# summary = llm_summary(context)
summary = "이 사업은 2025년까지 무인도서 정보관리시스템의 유지관리 및 데이터베이스 현행화를 목표로 합니다. 무인도서 실태조사 결과를 DB에 입력하고, 종합정보시스템의 운영 및 유지관리를 수행합니다. 사용자 편의를 위한 UI/UX 개선과 정보 표출 서비스 기능 추가도 포함됩니다. 또한, 해양관광 및 레저 개발을 위한 체계적 관리체계 구축이 필요합니다. 총 예산은 428,000,000원이며, 경쟁입찰 방식으로 진행됩니다."
category_dict = llm_category_classification(summary)
print(summary)
print(category_dict)
pass
