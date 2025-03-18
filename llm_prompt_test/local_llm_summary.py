from langchain_core.output_parsers import JsonOutputParser,StrOutputParser
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from langchain_ollama import ChatOllama
from function_list.langsmith_log import langsmith
from dotenv import load_dotenv
import json


def create_langchain_documents(docs):
    """
    텍스트 문서 리스트를 LangChain Document 객체 리스트로 변환합니다.

    Args:
        docs (list): 텍스트 문서 리스트

    Returns:
        list: LangChain Document 객체 리스트
    """
    return [Document(page_content=text, metadata={}) for text in docs]


def llm_summary(text,llm_name):
    """
    공고 텍스트를 분석하여 JSON 형식으로 요약을 생성합니다.

    Args:
        text (str): 분석할 공고 텍스트

    Returns:
        dict: 요약 결과(JSON 형식)
    """
    # 환경 변수 로드
    load_dotenv()

    langsmith(llm_name)

    # 프롬프트 템플릿 정의
    prompt_template = """이 공고의 **사업(과업) 수행 내용**을 요약해주세요.

### 제공된 공고 내용:
{context}

### 출력 형식(JSON):
```json
{{"summary": "공고의 사업(과업) 수행 내용을 5줄로 요약한 내용입니다."}}
```

### 요약 작성 규칙:
1. "summary" 필드는 항상 5줄 이내로 작성합니다.
2. 요약 내용은 반드시 "~입니다." 형식으로 끝납니다.
- 예시: '이 사업은 AI 기술을 활용하여 데이터를 분석하는 과업을 포함하고 있습니다.'

"""
    # LLM 모델 초기화
    llm = ChatOllama(
        model=llm_name,
        format="json",  # 입출력 형식을 JSON으로 설정합니다.
        temperature=0
    )

    # JSON 파서 초기화
    parser = JsonOutputParser()

    try:
        # 프롬프트 생성 및 LLM 호출
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm | parser
        response = chain.invoke({"context":text})

        # 응답 파싱
        # parsed_output = parser.parse(response.content)
        return response['summary']

    except Exception as e:
        print(f"[오류] LLM 호출 실패: {e}")
        return {"error": "LLM 호출 중 오류가 발생했습니다."}


# # 사용 예시
# if __name__ == "__main__":
#     # 샘플 공고 텍스트
#     sample_text = """
#     2024년도 인공지능 산업 육성 사업 공고
#     사업기간: 2024년 4월 1일 ~ 2024년 12월 31일
#     지원대상: AI 기술 개발 기업
#     지원내용: 기업당 최대 5천만 원 지원
#     신청방법: 온라인 접수
#     """

#     # 요약 실행
#     result = llm_summary(sample_text)

#     # 결과 출력
#     print(json.dumps(result, ensure_ascii=False, indent=2))
