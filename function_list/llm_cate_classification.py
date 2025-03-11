from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from function_list.langsmith_log import langsmith
from dotenv import load_dotenv

def create_langchain_documents(docs):
    # LangChain Document 객체 리스트 생성
    documents = []
    for text in docs:
        # 각 섹션에 대해 Document 객체 생성
        # if section_cate_list != None:
        doc = Document(
            page_content=text,  # 섹션의 텍스트 내용
            metadata={}  # 섹션 이름을 메타데이터로 추가
        )
        documents.append(doc)
    return documents

def llm_category_classification(text):
    # API KEY 정보로드
    load_dotenv()

    # 프로젝트 이름을 입력합니다.
    langsmith("g2b_notice_test_1")

    text= text[:4000]
    text_list = text.split('\n')[:-1]
    context='\n'.join(text_list)

    # 문서에 포함되어 있는 정보를 검색하고 생성합니다.
    # 프롬프트를 생성합니다.
    prompt = PromptTemplate.from_template(
            """
            이 공고의 카테고리를 IT 관련 기술(예시: 인공지능, 클라우드, 데이터베이스)을 기준으로 분류해주세요. 카테고리가 '없음'일 경우, 빈 리스트로 남겨주세요.
            
            ### 제공된 공고 내용:
            {context}

            ### 출력 형식(JSON):

            ```
            “category": [
                
                “name": “[한국어로 된 카테고리 이름]”,
                “참조_텍스트": “[발견된 관련 텍스트]
            ```

            """)


    # ChatOpenAI (LLM) 생성 시 API 키 전달
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser()

    # 체인 실행
    response = llm.invoke(prompt.format(context=context))

    parsed_output = parser.parse(response.content)
    category_dict = parsed_output['category']
    category_list = [category['name'] for category in category_dict]
    return category_dict,category_list