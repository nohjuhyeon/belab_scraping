from dotenv import load_dotenv
import pandas as pd 
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from function_list.g2b_func_test_second import detect_file_type, notice_keyword_search
from llm_prompt_test.local_llm_summary import llm_summary
from llm_prompt_test.local_llm_cate_classification import llm_category_classification
from langchain_ollama import ChatOllama
import json
# MongoDB 연결 설정
load_dotenv()

llm_list = ['EEVE-Korean-Instruct-10.8B:latest']
# llm_list = ['llama-3.2-Korean-Bllossom-3B:latest','ko-gemma-2:latest','EEVE-Korean-Instruct-10.8B:latest']
file_list = ['belab_scraping/test.hwp','belab_scraping/test.hwpx','belab_scraping/test2.hwp','belab_scraping/test2.hwpx','belab_scraping/test3.hwpx']
for llm_element in llm_list:
    for file_path in file_list:
        text = detect_file_type(file_path)
        text= text[:4000]
        text_list = text.split('\n')[:-1]
        context='\n'.join(text_list)
        # LLM 모델 초기화
        print("LLM model: ", llm_element)
        # notice_type = notice_keyword_search(context)
        summary = llm_summary(context,llm_element)
        print(summary)
        category_dict = llm_category_classification(summary,llm_element)
        print(category_dict)
        print("-"*100)
        pass
    print("="*100)
