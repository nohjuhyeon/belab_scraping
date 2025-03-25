from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from function_list.langsmith_log import langsmith
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig


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


def llm_category_classification(text):
    # API KEY 정보로드
    load_dotenv()

    # 프로젝트 이름을 입력합니다.
    # langsmith("gpt_4o_mini")

    # 문서에 포함되어 있는 정보를 검색하고 생성합니다.
    # 프롬프트를 생성합니다.
    prompt = PromptTemplate.from_template(
        """
        다음은 공고의 요약문입니다.  
        이 요약문에서 요구하는 **IT 관련 기술**(예시: 인공지능, 클라우드, 데이터베이스)을 분류해주세요.  
        단, 아래 조건을 반드시 준수하여 IT 관련 기술을 정확히 분류하세요:  


        ## **분류 조건**  

        1. **IT 관련 기술로 인정되는 경우**  
        - 기술이 명확히 언급되거나, 기술의 구현 또는 활용이 구체적으로 요구되는 경우.  
        - 예를 들어, "데이터베이스 구축 및 유지보수", "클라우드 기반 시스템 설계"와 같이 특정 IT 기술의 적용이 필요한 과업.  

        2. **IT 관련 기술로 인정되지 않는 경우**  
        - 단순히 **데이터 입력**, **데이터 점검**, **기초 통계 분석**과 같은 비기술적 작업.  
        - **IT 교육 커리큘럼 개발**이나 **IT 관련 교육 제공**과 같은 간접적인 활동.  
        - **시설 점검**, **공사 관리**, **단순 모니터링** 등 IT 기술의 활용이 아닌 일반 업무.  

        3. **기술이 포함될 수 있는 경우**  
        - 기술의 구체적인 활용이 언급되었거나, 기술적 작업이 암시되는 경우만 포함.  
        - 예: "클라우드 환경에서 데이터 관리 시스템 구축"은 포함되지만, "데이터 관리"만 언급된 경우 제외.  



        ## **IT 관련 기술**:
            1. **인공지능**  
            인간의 지능을 모방하여 학습, 추론, 문제 해결 등을 수행하는 기술.

            2. **데이터베이스**  
            데이터베이스를 구축하고, 유지 및 장애 처리를 수행하는 기술.

            3. **클라우드 컴퓨팅**  
            인터넷을 통해 컴퓨팅 자원(서버, 스토리지 등)을 제공하고 관리하는 기술.

            4. **소프트웨어 개발 및 관리**  
            소프트웨어를 설계, 구현, 테스트 및 유지보수하는 과정과 관련 기술.

            5. **네트워크 및 보안**  
            디지털 통신 네트워크의 설계, 운영, 최적화와 데이터 보호를 위한 보안 기술 및 솔루션.

            6. **IoT**  
            인터넷에 연결된 물리적 디바이스와 센서를 통해 데이터를 수집하고 상호작용하는 기술.

            7. **블록체인**  
            거래 기록을 분산 원장에 저장하여 투명성과 보안을 강화하는 기술.

            8. **AR/VR 및 메타버스**  
                증강현실과 가상현실 기술을 활용한 몰입형 가상 환경과 메타버스 플랫폼 기술.

            9. **기타 기술**  
                미래 기술(양자 컴퓨팅, 5G 등)과 특수 목적의 새로운 IT 기술.

        
        ### 제공된 공고 요약문 내용:
        {context}

        ### 출력 형식(JSON):

        ```
        “IT 관련 기술": [
            
            “name": “[한국어로 된 카테고리 이름]”,
            “참조_텍스트": “[발견된 관련 텍스트]
        ```

        ### **주의사항**  
        - IT 관련 기술이 언급되지 않은 경우, 빈 리스트로 남겨주세요.  
        - 공사, 점검, 데이터 입력, 교육 커리큘럼 개발과 같은 활동은 IT 관련 기술로 포함하지 마세요.  
        - 기술의 이름이 명확히 언급되지 않았더라도, 기술적 활용이 구체적으로 암시된 경우에만 포함하세요.  

            """
    )

    # ChatOpenAI (LLM) 생성 시 API 키 전달
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser()

    llm_tag = RunnableConfig(tags=["classification", "gpt-4o-mini"])
    # 체인 실행
    response = llm.invoke(prompt.format(context=text), config=llm_tag)

    parsed_output = parser.parse(response.content)
    category_dict = parsed_output["IT 관련 기술"]
    category_list = [category["name"] for category in category_dict]
    return category_dict, category_list
