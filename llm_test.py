from dotenv import load_dotenv
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from function_list.g2b_func_test_second import detect_file_type, notice_keyword_search
from function_list.llm_summary import llm_summary
from function_list.llm_cate_classification import llm_category_classification
from function_list.basic_options import mongo_setting
import json

# MongoDB 연결 설정
load_dotenv()

import json

# JSON 파일 경로
file_path = "notice_test.json"

# JSON 파일을 딕셔너리로 불러오기
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)


data
new_dict = []

collection = mongo_setting("news_scraping", "llm_notice")
results = collection.find({}, {"_id": 0, "notice_id": 1})
id_list = [i["notice_id"] for i in results]

for i in data:
    if i["notice_id"] not in id_list:
        context = i["notice_text"]
        # LLM 모델 초기화
        # notice_type = notice_keyword_search(context)
        summary = llm_summary(context)
        print(summary)
        category_dict, category_list = llm_category_classification(summary)
        print(category_dict)
        print("-" * 100)
        i["llm_summary"] = summary
        i["llm_category"] = category_dict
        collection.insert_one(
            {
                "notice_id": i["notice_id"],
                "notice_text": i["notice_text"],
                "llm_summary": summary,
                "llm_category": category_dict,
            }
        )
        pass

with open(file_path, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
