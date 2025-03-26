from langchain_core.output_parsers import JsonOutputParser,StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from function_list.langsmith_log import langsmith
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
from langchain.output_parsers.enum import EnumOutputParser
from enum import Enum

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
            이 공고가 소프트웨어 기업업이 참여할 수 있는 사업인지 분류해주세요. 
            참여할 수 있으면 True, 없으면 False로 응답해주세요.

            ### 제공된 공고 내용:
            {context}
            
            ### Instructions: 
            {instructions}
            """
    ).partial(instructions=parser.get_format_instructions())

    # ChatOpenAI (LLM) 생성 시 API 키 전달
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    # parser = StrOutputParser()
    chain = prompt | llm | parser
    response = chain.invoke({"context":text})    

    return response.value