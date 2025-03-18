from dotenv import load_dotenv
import pandas as pd 
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from function_list.g2b_func_test_second import detect_file_type, notice_keyword_search, llm_category_classification, llm_summary
import json
# MongoDB 연결 설정
load_dotenv()

file_path = 'test.hwpx'
text = detect_file_type(file_path)
text= text[:4000]
text_list = text.split('\n')[:-1]
context='\n'.join(text_list)

# notice_type = notice_keyword_search(context)
summary = llm_summary(context)
category_dict = llm_category_classification(summary)
print(summary)
print(category_dict)
pass