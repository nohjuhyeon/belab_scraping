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
    langsmith("g2b_notice_test_2")

    text= text[:4000]
    text_list = text.split('\n')[:-1]
    context='\n'.join(text_list)

    # 문서에 포함되어 있는 정보를 검색하고 생성합니다.
    # 프롬프트를 생성합니다.
    prompt = PromptTemplate.from_template(
            """
            이 공고의 사업(과업) 추진 내용을 요약해주세요. 공고의 추진 내용에 IT 관련 기술이 포함될 경우, 카테고리를 IT 관련 기술을 기준으로 분류해주세요. IT 관련 기술이 포함되지 않을 경우, 빈 리스트로 남겨주세요.

            ---

            ## **IT 관련 기술**:
            1. **인공지능**  
            인간의 지능을 모방하여 학습, 추론, 문제 해결 등을 수행하는 기술.

            2. **데이터베이스**  
            데이터를 저장, 관리, 검색 및 최적화하기 위한 시스템과 기술.

            3. **클라우드 컴퓨팅**  
            인터넷을 통해 컴퓨팅 자원(서버, 스토리지 등)을 제공하고 관리하는 기술.

            4. **소프트웨어 개발**  
            소프트웨어를 설계, 구현, 테스트 및 유지보수하는 과정과 관련 기술.

            5. **네트워크 및 보안**  
            디지털 통신 네트워크의 설계, 운영, 최적화와 데이터 보호를 위한 보안 기술 및 솔루션.

            6. **데이터 분석 및 데이터 과학**  
            데이터를 수집, 처리, 분석하여 유의미한 통찰을 도출하는 기술과 방법론.

            7. **IoT**  
            인터넷에 연결된 물리적 디바이스와 센서를 통해 데이터를 수집하고 상호작용하는 기술.

            8. **블록체인**  
            거래 기록을 분산 원장에 저장하여 투명성과 보안을 강화하는 기술.

            9. **가상화 및 컨테이너 기술**  
            물리적 하드웨어를 가상화하거나 애플리케이션을 컨테이너로 격리하여 실행하는 기술.

            10. **소프트웨어 테스트 및 품질 관리**  
                소프트웨어의 결함을 발견하고 품질을 보장하기 위한 테스트 및 관리 기술.

            11. **AR/VR 및 메타버스**  
                증강현실과 가상현실 기술을 활용한 몰입형 가상 환경과 메타버스 플랫폼 기술.

            12. **IT 운영 및 관리**  
                IT 시스템의 안정적 운영, 모니터링, 복구 및 서비스 관리 기술.

            13. **기타 기술**  
                미래 기술(양자 컴퓨팅, 5G 등)과 특수 목적의 새로운 IT 기술.

            ---

            ### 제공된 공고 내용:
            {context}

            ---

            ### **출력 형식(JSON)**:

            ```json
                "summary": "공고의 사업(과업) 수행 내용을 5줄로 요약한 내용입니다.",
                "category": [
                        "name": "[한국어로 된 카테고리 이름]",
                        "참조_텍스트": "[발견된 관련 텍스트]"
                ]
            ```

            ### **요약 작성 규칙**:
            1. `"summary"` 필드는 항상 **5줄 이내**로 작성합니다.
            2. 요약 내용은 반드시 **"~입니다."** 형식으로 끝납니다.
            - 예시: "이 사업은 AI 기술을 활용하여 데이터를 분석하는 과업을 포함하고 있습니다."
            3. 공고 내용에 IT 관련 기술이 포함되지 않을 경우, `"category"`는 빈 리스트로 작성합니다.

            """)


    # ChatOpenAI (LLM) 생성 시 API 키 전달
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser()

    # 체인 실행
    response = llm.invoke(prompt.format(context=context))

    parsed_output = parser.parse(response.content)
    summary = parsed_output['summary']
    category_dict = parsed_output['category']
    category_list = [category['name'] for category in category_dict]
    return category_dict,category_list,summary