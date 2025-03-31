from langchain_core.output_parsers import JsonOutputParser,StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from function_list.langsmith_log import langsmith
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
from langchain.output_parsers.enum import EnumOutputParser
from enum import Enum
import time

class it_notice(Enum):
    TRUE = "True"
    FALSE = "False"
    
# EnumOutputParser 인스턴스 생성
parser = EnumOutputParser(enum=it_notice)


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


def llm_it_notice_check(text):
    # API KEY 정보로드
    load_dotenv()

    # 프로젝트 이름을 입력합니다.
    langsmith("gpt_4o_mini")

    # 문서에 포함되어 있는 정보를 검색하고 생성합니다.
    # 프롬프트를 생성합니다.
    prompt = PromptTemplate.from_template(
        """
        이 공고가 소프트웨어 회사가 참여할 수 있는 프로젝트인지 분류해 주세요.  
        IT와 관련된 경우라도, 영상 콘텐츠 개발, 행사 주최, 행사 운영, 교육 프로그램 개발과 같은 작업이 포함되어 있다면 참여할 수 없습니다.  
        참여할 수 있는 경우 **반드시** "True"만 응답하고, 참여할 수 없는 경우 **반드시** "False"만 응답하세요.  
        추가적인 설명은 포함하지 마세요.

        ### 제공된 공고 내용:
        {context}
        
        ### 지시 사항: 
        {instructions}
        """
    ).partial(instructions=parser.get_format_instructions())

    # ChatOpenAI (LLM) 생성 시 API 키 전달
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    # parser = StrOutputParser()
    start_time = time.time()  # 시작 시간 기록

    response = llm.invoke(prompt.format(context=text))    

    parsed_output = parser.parse(response.content)

    end_time = time.time()  # 종료 시간 기록
    execution_time = end_time - start_time

    return parsed_output.value,execution_time,response.usage_metadata