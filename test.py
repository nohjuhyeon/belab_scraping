from dotenv import load_dotenv
import pandas as pd 
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
# MongoDB 연결 설정
load_dotenv()

test_df = pd.read_csv('test.csv')
data = test_df.to_dict('records')  # 레코드 형식의 딕셔너리 리스트

prompt = PromptTemplate.from_template(
        """
        다음은 공고의 요약문입니다.
        이 요약문에서 요구하는 IT 관련 기술(예시: 인공지능, 클라우드, 데이터베이스)을 분류해주세요. 출력 양식은 아래를 참고해주세요. 없을 경우, 빈 리스트로 남겨주세요.

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

        
        ### 제공된 공고 요약문 내용:
        {context}

        ### 출력 형식(JSON):

        ```
        “IT 관련 기술": [
            
            “name": “[한국어로 된 카테고리 이름]”,
            “참조_텍스트": “[발견된 관련 텍스트]
        ```

""")


# ChatOpenAI (LLM) 생성 시 API 키 전달
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
parser = JsonOutputParser()
new_data = []
# 체인 실행
for i in data:
    context = i['summary']
    response = llm.invoke(prompt.format(context=context))
    parsed_output = parser.parse(response.content)
    print(context)
    print(parsed_output['IT 관련 기술'])
    new_dict = i
    new_dict['summary_cate_dict'] = parsed_output['IT 관련 기술']
    new_dict['summary_cate_list'] = [element['name'] for element in parsed_output['IT 관련 기술']]
    new_data.append(new_dict)
    print('----------------------------------------------------------------')

pass
with open('complex.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)

pass