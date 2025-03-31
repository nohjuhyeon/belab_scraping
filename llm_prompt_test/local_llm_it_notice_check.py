from langchain_core.output_parsers import JsonOutputParser,StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from function_list.langsmith_log import langsmith
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain.output_parsers.enum import EnumOutputParser
from enum import Enum
import time


def create_langchain_documents(docs):
    # LangChain Document 객체 리스트 생성
    documents = []
    for text in docs:
        # 각 섹션에 대해 Document 객체 생성
        # if section_cate_list != None:
        doc = Document(
            page_content=text,  # 섹션의 텍스트 내용
            metadata={},  # 섹션 이름을 메타데이터로 추가
        )
        documents.append(doc)
    return documents


def llm_it_notice_check(text,llm_name):
    # API KEY 정보로드
    load_dotenv()

    # 문서에 포함되어 있는 정보를 검색하고 생성합니다.
    # 프롬프트를 생성합니다.
    prompt = PromptTemplate.from_template(
        """
        Please classify whether this notice is a project that software companies can participate in. 
        Even if it is related to IT, if it includes tasks such as video content development, event hosting, event management, or educational program development, they cannot participate. 
        If they can participate, respond with **only** "True". If they cannot participate, respond with **only** "False".
        Do not include any additional explanation.

        ### Provided Notice Content:
        {context}
        
        ### Output Format (JSON):
        ```json
        {{"it_notice": "Output True if it is related to IT, otherwise output False."}}
        ```      
        """
    )

    parser = JsonOutputParser()
    llm = ChatOllama(
        model=llm_name,
        format="json",  # 입출력 형식을 JSON으로 설정합니다.
        temperature=0
    )
    # parser = StrOutputParser()
    start_time = time.time()  # 시작 시간 기록
    response = llm.invoke(prompt.format(context=text))
    parsed_output = parser.parse(response.content)
    end_time = time.time()  # 종료 시간 기록
    execution_time = end_time - start_time
    try:
        total_tokens = response.usage_metadata['total_tokens']
    except:
        total_tokens = None
    return parsed_output['it_notice'],execution_time,total_tokens