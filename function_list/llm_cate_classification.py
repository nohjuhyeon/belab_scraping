from langchain.schema import Document
from function_list.langsmith_log import langsmith
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from enum import Enum
from typing import List
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain.output_parsers.enum import EnumOutputParser
from langchain_core.runnables import RunnableConfig
import time
class it_tech(Enum):
    AI = "인공지능(학습, 추론, 문제 해결 수행 기술)과 관련된 기술"
    database = "데이터베이스(데이터 저장, 관리, 검색 시스템)와 관련된 기술"
    cloud = "클라우드 컴퓨팅(인터넷 기반 컴퓨팅 자원 관리)과 관련된 기술"
    software_develop = "소프트웨어 개발(소프트웨어 설계, 구현, 테스트)와 관련된 기술"
    network_security = "네트워크/보안(통신 네트워크, 데이터 보호 기술)와 관련된 기술"
    data_analysis = "데이터 분석/과학(데이터 수집, 처리, 분석 기술)와 관련된 기술"
    IoT = "IoT(인터넷 연결 디바이스, 센서 기술)와 관련된 기술"
    blockchain = "블록체인(분산 원장 기술)와 관련된 기술"
    virtualization = "가상화/컨테이너(하드웨어 가상화, 컨테이너 기술)와 관련된 기술"
    sw_test = "SW 테스트/품질(소프트웨어 테스트, 품질 관리)와 관련된 기술"
    vr_ar = "AR/VR/메타버스(증강현실, 가상현실 기술)와 관련된 기술"
    it_management = "IT 운영/관리(시스템 운영, 모니터링, 관리)와 관련된 기술"
    others = "기타(양자 컴퓨팅, 5G 등 신기술)와 관련된 기술"

def create_langchain_documents(docs):
    documents = []
    for text in docs:
        doc = Document(
            page_content=text,
            metadata={}
        )
        documents.append(doc)
    return documents

def llm_category_classification(text) -> List[str]:
    load_dotenv()

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
        - **IT 교육 커리큘럼 개발**이나 **IT 관련 교육 제공**, **IT 관련 전문 인력 개발**과 같은 간접적인 활동.  
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


    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    try:
        # response = llm.invoke(prompt.format(context=text))
        # prompt = ChatPromptTemplate.from_template(prompt_template)
        parser = JsonOutputParser()

        # 체인 실행
        start_time = time.time()  # 시작 시간 기록
        response = llm.invoke(prompt.format(context=text))

        parsed_output = parser.parse(response.content)
        # selector_list = ['AI','cloud','data_analysis','software_develop','database','network_security','IoT','blockchain','virtualization','sw_test','vr_ar','it_management','others']
        # categories =[]
        # for selector_element in selector_list:
        #     if selector_element in response.content:
        #         categories.append(selector_element)
        category_dict = []
        for i in parsed_output['IT 관련 기술']:
            if i['참조_텍스트'] != '' and i['참조_텍스트'] is not None:
                category_dict.append(i)
        category_list = [category["name"] for category in category_dict]
        end_time = time.time()  # 종료 시간 기록
        execution_time = end_time - start_time

        return category_dict,category_list,execution_time,response.usage_metadata
            
    except Exception as e:
        print(f"Error processing response: {e}")
        return [], []
