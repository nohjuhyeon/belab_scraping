import zipfile
import shutil
import os 
from function_list.hwp_loader import HWPLoader
from function_list.hwpx_loader import get_hwpx_text
from langchain_community.document_loaders import PyPDFLoader
from function_list.llm_summary import llm_summary
from function_list.llm_cate_classification import llm_category_classification
from function_list.llm_it_notice_check import llm_it_notice_check

# 폴더 내 파일 및 디렉토리 정리 함수
def folder_clear(download_folder_path):
    """
    지정된 폴더 내 모든 파일 및 디렉토리를 삭제합니다.

    Args:
        download_folder_path (str): 삭제할 폴더 경로.
    """
    for filename in os.listdir(download_folder_path):
        file_path = os.path.join(download_folder_path, filename)
        try:
            # 파일인지 확인하고 삭제
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 디렉토리 삭제
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

# 공고 파일 확인 및 처리 함수
def notice_file_check(download_folder_path):
    """
    다운로드 폴더 내 공고 파일을 확인하고, 키워드 기반으로 공고 유형, 분류 정보, 요약을 반환합니다.

    Args:
        download_folder_path (str): 다운로드 폴더의 경로.

    Returns:
        tuple:
            - notice_type(:ist[str]): 공고 파일에서 추출된 공고 유형 리스트.
            - category_dict(dict): 키워드 기반으로 분류된 공고 정보.
            - category_list(List[str]): 공고가 속하는 카테고리 리스트.
            - summary(str): 공고 내용을 요약한 텍스트.
            - text(str): 공고 본문
    """
    
    category_dict = []  # 분류 결과 저장
    category_list = []  # 분류된 카테고리 리스트
    summary = ''  # 요약 저장
    context = ''  # 텍스트 컨텍스트 저장
    text=''
    it_notice_check=''
    for file_name in os.listdir(download_folder_path):
        file_path = os.path.join(download_folder_path, file_name)
        # ZIP 파일 처리
        if file_name.lower().endswith('.zip'):
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    for file_info in zip_ref.infolist():
                        # 파일 이름을 CP949로 디코딩 후 UTF-8로 재인코딩
                        try:
                            decoded_name = file_info.filename.encode('cp437').decode('cp949')
                        except UnicodeEncodeError:
                            # cp437 인코딩을 건너뛰고 바로 cp949로 디코딩
                            decoded_name = file_info.filename                        
                        file_info.filename = decoded_name  # 파일 이름 수정
                        # 압축 해제할 경로
                        extract_path = os.path.join(download_folder_path)
                        zip_ref.extract(file_info, extract_path)
                os.remove(file_path)  # ZIP 파일 삭제
            except:
                pass

    # 키워드 파일 선택
    keyword_file = notice_file_select(download_folder_path)
    if keyword_file.replace('/n','').replace(' ','') != '':
        file_path = os.path.join(download_folder_path, keyword_file)
        # 파일 유형 감지 및 텍스트 추출
        text = detect_file_type(file_path)
        text_4000 = text[:4000]  # 텍스트 길이 제한
        text_list = text_4000.split('\n')[:-1]
        context = '\n'.join(text_list)

        # IT 공고 여부 확인
        it_notice_check, check_time, check_token = llm_it_notice_check(context)
        if it_notice_check.lower() == 'true':
            # 요약 생성
            summary, summary_time, summary_token = llm_summary(context)
            # 카테고리 분류
            category_dict, category_list, category_time, category_token = llm_category_classification(summary)
    return it_notice_check, category_dict, category_list, summary,text

# 파일 유형 감지 및 텍스트 추출 함수
def detect_file_type(file_path):
    """
    파일 유형을 감지하고, 해당 파일에서 텍스트를 추출합니다.

    Args:
        file_path (str): 파일 경로.

    Returns:
        str: 추출된 텍스트 또는 오류 메시지.
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)  # 파일의 처음 8바이트 읽기

            # HWP 파일 확인
            if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
                loader = HWPLoader(file_path)
                docs = loader.load()
                content = docs[0].page_content
                return content
            
            # HWPX 파일 확인
            elif header.startswith(b'\x50\x4B\x03\x04'):
                content, metadata = get_hwpx_text(file_path)
                content = '\n\n'.join(content)
                return content

            # PDF 파일 확인
            elif header.startswith(b'%PDF'):
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                content_list = [doc.page_content for doc in docs]
                content = ' \n'.join(content_list)
                return content

            # 기타 파일
            else:
                return "Unknown"
    except Exception as e:
        return f"Error detecting file type: {e}"

# 텍스트 내 특정 키워드 검색 함수
def search_keywords_in_text(text, keywords):
    """
    텍스트 내 특정 키워드가 포함되어 있는지 확인합니다.

    Args:
        text (str): 검색할 텍스트.
        keywords (list): 키워드 리스트.

    Returns:
        bool: 키워드가 포함되어 있으면 True, 아니면 False.
    """
    if text:
        for keyword in keywords:
            if keyword in text:
                return True
    return False

# 공고 파일 선택 함수
def notice_file_select(download_folder_path):
    """
    다운로드 폴더 내에서 특정 키워드를 포함한 파일을 선택합니다.

    Args:
        download_folder_path (str): 다운로드 폴더 경로.

    Returns:
        keyword_file(str): 선택된 파일 이름.
    """
    keyword_file = ''
    for file_name in os.listdir(download_folder_path):
        # 파일 이름에서 특정 키워드 검색
        if 'requestfortask' in file_name or 'statementofwork' in file_name or 'taskorder' in file_name:
            keyword_file = file_name
        elif 'requestforproposal' in file_name and keyword_file == '':
            keyword_file = file_name 
    return keyword_file

# 텍스트에서 공고 키워드 검색 함수
def notice_keyword_search(text):
    """
    텍스트에서 공고와 관련된 키워드를 검색하여 유형을 분류합니다.

    Args:
        text (str): 검색할 텍스트.

    Returns:
        notice_type(List[str]): 공고 유형 리스트.
    """
    ai_keywords = ['AI', '인공지능', 'LLM', '생성형', '초거대', '언어 모델', '언어모델', '챗봇']
    db_keywords = ['Database', '데이터 레이크', '빅데이터', '데이터 허브', '데이터베이스']
    cloud_keywords = ['클라우드', 'cloud']
    notice_type = []

    # 키워드 검색 및 유형 추가
    if search_keywords_in_text(text, ai_keywords) and '인공지능' not in notice_type:
        notice_type.append('인공지능')
    if search_keywords_in_text(text, db_keywords) and '데이터' not in notice_type:
        notice_type.append('데이터')
    if search_keywords_in_text(text, cloud_keywords) and '클라우드' not in notice_type:
        notice_type.append('클라우드')

    return notice_type

# 공고 제목에서 키워드 검색 함수
def notice_title_check(notice_title,category_list):
    """
    공고 제목에서 키워드를 검색하여 유형을 분류합니다.

    Args:
        notice_title (str): 공고 제목.

    Returns:
        notice_type(List[str]): 공고 유형 리스트.
    """

    isp_keywords = ['ISP', 'ISMP']

    # 키워드 검색 및 유형 추가
    if search_keywords_in_text(notice_title, isp_keywords) and 'ISP/ISMP' not in category_list:
        category_list.append('ISP/ISMP')

    return category_list
