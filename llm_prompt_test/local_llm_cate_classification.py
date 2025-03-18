from langchain.schema import Document
from function_list.langsmith_log import langsmith
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from enum import Enum
from typing import List
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain.output_parsers.enum import EnumOutputParser

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
    langsmith("local_llm_test")

    prompt_template = """
제공된 공고 요약문에서 요구하는 IT 관련 기술을 Instructions에 맞게 분류해주세요.
발견된 기술 이름과 해당 기술이 언급된 참조 텍스트를 포함해야 합니다.
만약 IT 관련 기술이 없는 경우, 해당 기술의 "name"과 "참조_텍스트"는 제외해주세요.

### 제공된 공고 요약문:
{context}

### Instructions:
1. 인공지능: 인간의 지능을 모방하여 학습, 추론, 문제 해결 등을 수행하는 기술.
2. 데이터베이스: 데이터를 저장, 관리, 검색 및 최적화하기 위한 시스템과 기술.
3. 클라우드 컴퓨팅: 인터넷을 통해 컴퓨팅 자원(서버, 스토리지 등)을 제공하고 관리하는 기술.
4. 소프트웨어 개발: 소프트웨어를 설계, 구현, 테스트 및 유지보수하는 과정과 관련 기술.
5. 네트워크 및 보안: 디지털 통신 네트워크의 설계, 운영, 최적화와 데이터 보호를 위한 보안 기술 및 솔루션.
6. 데이터 분석 및 데이터 과학: 데이터를 수집, 처리, 분석하여 유의미한 통찰을 도출하는 기술과 방법론.
7. IoT: 인터넷에 연결된 물리적 디바이스와 센서를 통해 데이터를 수집하고 상호작용하는 기술.
8. 블록체인: 거래 기록을 분산 원장에 저장하여 투명성과 보안을 강화하는 기술.
9. 가상화 및 컨테이너 기술: 물리적 하드웨어를 가상화하거나 애플리케이션을 컨테이너로 격리하여 실행하는 기술.
10. 소프트웨어 테스트 및 품질 관리: 소프트웨어의 결함을 발견하고 품질을 보장하기 위한 테스트 및 관리 기술.
11. AR/VR 및 메타버스: 증강현실과 가상현실 기술을 활용한 몰입형 가상 환경과 메타버스 플랫폼 기술.
12. IT 운영 및 관리: IT 시스템의 안정적 운영, 모니터링, 복구 및 서비스 관리 기술.
13. 기타 기술: 미래 기술(양자 컴퓨팅, 5G 등)과 특수 목적의 새로운 IT 기술.

### 출력 형식(JSON):
```json
{{"IT 관련 기술": [
        {{"name": "한국어로 된 카테고리 이름"}},
        {{"참조_텍스트": "발견된 관련 텍스트"}}
    ]
}}
```
"""

    llm = ChatOllama(
        model="EEVE-Korean-Instruct-10.8B:latest",
        format="json",  # 입출력 형식을 JSON으로 설정합니다.
        temperature=0
    )

    parser = EnumOutputParser(enum=it_tech)
    try:
        # response = llm.invoke(prompt.format(context=text))
        prompt = PromptTemplate.from_template(prompt_template)
        # prompt = ChatPromptTemplate.from_template(prompt_template)
        parser = JsonOutputParser()
        chain = prompt | llm | parser
        response = chain.invoke({"context":text})

        # selector_list = ['AI','cloud','data_analysis','software_develop','database','network_security','IoT','blockchain','virtualization','sw_test','vr_ar','it_management','others']
        # categories =[]
        # for selector_element in selector_list:
        #     if selector_element in response.content:
        #         categories.append(selector_element)
        category_list = []
        for i in response['IT 관련 기술']:
            if i['참조_텍스트'] != '' and i['참조_텍스트'] is not None:
                category_list.append(i)
        return category_list
            
    except Exception as e:
        print(f"Error processing response: {e}")
        return []
