from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain.schema import Document  # Document 객체를 사용하기 위해 추가
from function_list.g2b_func import detect_file_type, remove_chinese_characters, remove_control_characters

# 단계 1: 문서 로드(Load Documents)
text = detect_file_type("./test.hwpx")
text = remove_chinese_characters(text)
text = remove_control_characters(text)

# 문자열을 LangChain의 Document 객체로 변환
document = Document(page_content=text, metadata={"source": "./test.hwpx"})
print(f"문서의 페이지수: 1")  # 단일 문서이므로 페이지 수는 1로 고정

# 단계 2: 문서 분할(Split Documents)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_documents = text_splitter.split_documents([document])  # Document 객체의 리스트를 전달
print(f"분할된 청크의 수: {len(split_documents)}")

# Hugging Face 기반의 임베딩 생성기를 사용합니다.
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 벡터스토어를 생성합니다.
vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)
# for doc in vectorstore.similarity_search("구글"):
#     print(doc.page_content)
    
# 문서에 포함되어 있는 정보를 검색하고 생성합니다.
retriever = vectorstore.as_retriever()
# 검색기에 쿼리를 날려 검색된 chunk 결과를 확인합니다.
retriever.invoke("이 공고를 요약해줘")

# 프롬프트를 생성합니다.
prompt = PromptTemplate.from_template(
    """You are an AI assistant designed to summarize information from bid announcements.
Based on the retrieved context below, provide a concise summary of the requested information.
If the required information is not found in the retrieved context, respond with 'The requested information could not be found.'
Always answer in Korean.
#Context: 
{context}

#Question:
{question}

#Answer:"""
)
# Hugging Face 기반의 Llama 모델을 사용합니다.
llm = HuggingFacePipeline.from_model_id(
    model_id="meta-llama/Llama-2-7b-chat-hf",
    task="text-generation",
    model_kwargs={"temperature": 0},
    use_auth_token=True  # 인증 토큰 사용
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 체인 실행(Run Chain)
# 문서에 대한 질의를 입력하고, 답변을 출력합니다.
question = "이 공고를 요약해줘"
response = chain.invoke(question)
print(response)
