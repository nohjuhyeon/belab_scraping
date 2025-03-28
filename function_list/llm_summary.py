from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from function_list.langsmith_log import langsmith
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
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


def llm_summary(text):
    # API KEY 정보로드
    load_dotenv()

    # 프로젝트 이름을 입력합니다.
    # langsmith("gpt_4o_mini")

    # 문서에 포함되어 있는 정보를 검색하고 생성합니다.
    # 프롬프트를 생성합니다.
    prompt = PromptTemplate.from_template(
        """
            이 공고의 사업(과업) 추진 내용을 요약해주세요.

            ### 제공된 공고 내용:
            {context}

            ---

            ### **출력 형식(JSON)**:

            ```json
                "summary": "공고의 사업(과업) 수행 내용을 5줄로 요약한 내용입니다."
            ```

            ### **요약 작성 규칙**:
            1. `"summary"` 필드는 항상 **5줄 이내**로 작성합니다.
            2. 요약 내용은 반드시 **"~입니다."** 형식으로 끝납니다.
            - 예시: "이 사업은 AI 기술을 활용하여 데이터를 분석하는 과업을 포함하고 있습니다."
            """
    )

    # ChatOpenAI (LLM) 생성 시 API 키 전달
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser()

    llm_tag = RunnableConfig(tags=["summarization", "gpt-4o-mini"])

    start_time = time.time()  # 시작 시간 기록

    # 체인 실행
    response = llm.invoke(prompt.format(context=text), config=llm_tag)

    parsed_output = parser.parse(response.content)
    summary = parsed_output["summary"]
    
    end_time = time.time()  # 종료 시간 기록
    execution_time = end_time - start_time

    return summary,execution_time,response.usage_metadata['total_tokens']
