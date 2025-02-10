from function_list.g2b_func import detect_file_type, remove_chinese_characters, remove_control_characters
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from langchain_teddynote import logging

# 프로젝트 이름을 입력합니다.
logging.langsmith("CH01-Basic")

text = detect_file_type('(붙임2) 과업지시서.hwpx')
text = remove_chinese_characters(text)
text = remove_control_characters(text)
document = Document(page_content=text, metadata={"source": "(붙임2) 과업지시서.hwpx"})
pass

# 단계 2: 문서 분할(Split Documents)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_documents = text_splitter.split_documents([document])  # 여기서 []로 감싸야 함
print(f"분할된 청크의수: {len(split_documents)}")

# OpenAI Embeddings 생성 시 API 키 전달
embeddings = OpenAIEmbeddings(openai_api_key=openai_api)


# 벡터스토어를 생성합니다.
vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

# 문서에 포함되어 있는 정보를 검색하고 생성합니다.
retriever = vectorstore.as_retriever()
# 검색기에 쿼리를 날려 검색된 chunk 결과를 확인합니다.
retriever.invoke("공고의 요약문을 제공해줘")

# 프롬프트를 생성합니다.
prompt = PromptTemplate.from_template(
    """
    You are an expert in analyzing procurement announcements and determining whether your organization should participate in the project. Your task is to analyze the provided announcement, check if the project is related to **AI, data, relocation, cloud**, and summarize the **purpose and details of the project** concisely. If the project includes any relevant content, classify it into all applicable categories and provide the specific references (출처) **only from the "Project Description" section** of the announcement for the classification. **Do not include references from the title, metadata, or any other section outside of the "Project Description."** If the content does not fit into any category, select "None." The final answer must be written in Korean.

### Categories:
[AI, data, relocation, cloud, None]

### Announcement Content:
{context}

### Output Format:
- 사업 목적 및 내용 요약: [A concise summary of the purpose and details of the project in Korean]
- 카테고리: [A comma-separated list of all relevant categories in Korean]
- 분류 출처: [Provide specific text only from the "Project Description" section of the announcement that supports the selected categories in Korean. Do not include text from the title or metadata.]

""")

# ChatOpenAI (LLM) 생성 시 API 키 전달
llm = ChatOpenAI(model_name="gpt-4o", temperature=0, openai_api_key=openai_api)

chain = (
    {"context": retriever}
    | prompt
    | llm
    | StrOutputParser()
)

# 체인 실행(Run Chain)
# 문서에 대한 질의를 입력하고, 답변을 출력합니다.
question = "내용을 요약해줘"
response = chain.invoke(question)
print(response)