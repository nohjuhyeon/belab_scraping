from function_list.g2b_func import get_hwpx_text,get_hwp_text
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from langchain_teddynote import logging
from dotenv import load_dotenv
from test import HWPLoader, extract_tag_ids
# from kss import split_sentences

def section_category(text):
    section_cate_list = []
    for i in ['과업 목적','과업목적','사업목적','사업 목적']:
        if i in text and '사업 목적' not in section_cate_list:
            section_cate_list.append('사업 목적')
    for i in ['과업 내용','과업내용','사업내용','사업 내용']:
        if i in text and '사업 내용' not in section_cate_list:
            section_cate_list.append('사업 내용')
    for i in ['추진 배경','추진배경']:
        if i in text and '추진 배경' not in section_cate_list:
            section_cate_list.append('추진 배경')
    for i in ['참가 자격','참가자격']:
        if i in text and '참가 자격' not in section_cate_list:
            section_cate_list.append('참가 자격')
    if len(section_cate_list) != 0:
        return section_cate_list
    else:
        return None

def create_langchain_documents(docs, metadata):
    # LangChain Document 객체 리스트 생성
    documents = []
    for section, text in metadata.items():
        # 각 섹션에 대해 Document 객체 생성
        section_cate_list = section_category(text)
        # if section_cate_list != None:
        doc = Document(
            page_content=text,  # 섹션의 텍스트 내용
            metadata={"section": section,'category':section_cate_list}  # 섹션 이름을 메타데이터로 추가
        )
        documents.append(doc)
    return documents

# API KEY 정보로드
load_dotenv()

# 프로젝트 이름을 입력합니다.
logging.langsmith("CH01-Basic")

# extract_tag_ids('2. 2025년 한국전력공사 협업 광고대행사 선정 제안요청서(최종).hwp')

# # 단계 1: 파일 처리
# loader = HWPLoader('test.hwp')
# documents = loader.load()

docs, metadata = get_hwpx_text('test2.hwpx')
print(metadata)
documents = create_langchain_documents(docs, metadata)
pass

# 단계 2: 문서 분할(Split Documents)
text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=50)
split_documents = text_splitter.split_documents(documents)  # 여기서 []로 감싸야 함
print(f"분할된 청크의 수: {len(split_documents)}")


# OpenAI Embeddings 생성 시 API 키 전달
embeddings = OpenAIEmbeddings()


# 벡터스토어를 생성합니다.
vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

# 문서에 포함되어 있는 정보를 검색하고 생성합니다.
retriever = vectorstore.as_retriever()
# 검색기에 쿼리를 날려 검색된 chunk 결과를 확인합니다.
retrieved_docs  = retriever.invoke("사업 목적과 사업 내용, 추진 배경, 참가 자격에 대해 설명해줘")

# 프롬프트를 생성합니다.
prompt = PromptTemplate.from_template(
        """
귀하는 조달 공고를 분석하고 조직이 프로젝트에 참여해야 하는지 여부를 결정하는 전문가입니다. 귀사의 조직은 **AI, 클라우드, 데이터베이스**를 전문으로 하며, 제공된 공고를 분석하여 프로젝트가 **AI, 데이터, 이전 또는 클라우드**와 관련이 있는지 판단하는 것이 귀하의 임무입니다. 프로젝트의 **목적과 세부 내용을 간결하게 요약하세요**. 프로젝트에 관련 내용이 포함된 경우, 해당되는 모든 카테고리로 분류하고 공지의 '프로젝트 설명' 섹션에서만 **구체적인 참조를 제공하세요**. **제목, 메타데이터 또는 “프로젝트 설명” 외의 다른 항목에서는 언급하지 마세요."** 해당 내용이 어느 범주에도 해당하지 않거나 프로젝트가 **AI 또는 데이터 전문가 등 전문 인력 교육 또는 양성**과 관련된 경우, ‘없음’을 선택하고 다른 모든 범주를 제외하세요. 최종 답변은 **한국어**로 작성해야 합니다.

### 카테고리:
카테고리: [AI, 데이터, 이전, 클라우드, 없음]

#### 정의:
- AI**: 인공지능의 개발 또는 적용과 관련된 프로젝트.
- 데이터**: 데이터베이스의 구축, 운영 또는 관리와 관련된 프로젝트.
- 재배치**: 시스템, 인프라 또는 리소스의 물리적/디지털 이전과 관련된 프로젝트.
- 클라우드**: 클라우드 인프라의 구축, 운영 또는 관리와 관련된 프로젝트.

        “"”


### 제외 기준:
- AI 또는 데이터 전문가 등 **전문인력 양성 또는 교육**과 관련된 사업인 경우, 모든 항목을 제외하고 “없음”을 선택합니다.

### 제공된 공고 내용:
{context}

### 출력 형식(JSON):

```json

summary": “[프로젝트의 목적과 세부 사항을 한국어로 간결하게 요약한 내용]”,
  “category": [
    
      “name": “[한국어로 된 카테고리 이름]”,
      “reference": “[관련 텍스트가 발견된 청크 번호]”,
      “참조_텍스트": “[발견된 관련 텍스트]
“"”

""")



# ChatOpenAI (LLM) 생성 시 API 키 전달
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

chain = (
    {"context": retriever}
    | prompt
    | llm
    | JsonOutputParser()
)

# 체인 실행(Run Chain)
# 문서에 대한 질의를 입력하고, 답변을 출력합니다.
question = "내용을 요약해줘"
response = chain.invoke(question)

print(response)
print('----------------------------------------------------------------')
for i in retrieved_docs:
    print(i.page_content)
    print('----------------------------------------------------------------')
