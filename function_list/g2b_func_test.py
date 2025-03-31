import zipfile
import shutil
import os 
from function_list.hwp_loader import HWPLoader
from function_list.hwpx_loader import get_hwpx_text
import zipfile
from langchain_community.document_loaders import PyPDFLoader
from function_list.llm_cate_classification import llm_category_classification
from function_list.llm_it_notice_check import llm_it_notice_check
from function_list.llm_summary import llm_summary

def folder_clear(download_folder_path):
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

def notice_file_check(download_folder_path):
    notice_type = []
    category_dict= []
    category_list= []
    summary=''
    for file_name in os.listdir(download_folder_path):
        file_path = os.path.join(download_folder_path, file_name)
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
                        # 압축 해제할 임시 폴더 경로
                        extract_path = os.path.join(download_folder_path)
                        zip_ref.extract(file_info, extract_path)
                os.remove(file_path)
                pass
            except:
                pass
    keyword_file=notice_file_select (download_folder_path)    
    if keyword_file != '':
        file_path = os.path.join(download_folder_path, keyword_file)        
        text = detect_file_type(file_path)
        notice_type = notice_keyword_search(text)
        # it_notice_check,check_time,check_token = llm_it_notice_check(text)
        # if it_notice_check.lower() == 'true':
        #     summary,summary_time,summary_token = llm_summary(text)
        #     category_dict, category_list,category_time,category_token = llm_category_classification(summary)
    return notice_type
    # return notice_type,category_dict,category_list,summary


def detect_file_type(file_path):
    try:
        with open(file_path, 'rb') as f:
            # 파일의 처음 8바이트 읽기
            header = f.read(8)
            pass
            # HWP 파일 확인 (OLE2 매직 넘버)
            if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
                loader = HWPLoader(file_path)
                docs = loader.load()
                content = docs[0].page_content
                return content
            
            # HWPX 파일 확인 (ZIP 매직 넘버)
            elif header.startswith(b'\x50\x4B\x03\x04'):
                content,metadata = get_hwpx_text(file_path)
                content = '\n\n'.join(content)
                return content

            elif header.startswith(b'%PDF'):
                loader = PyPDFLoader(file_path)
                # PDF 로더 초기화
                docs = loader.load()
                content_list = []
                for i in docs:
                    content_list.append(i.page_content)
                content = ' \n'.join(content_list)
                return content

            # 기타 파일
            else:
                return "Unknown"
    except Exception as e:
        return f"Error detecting file type: {e}"


def search_keywords_in_text(text, keywords):
    """HWP 파일 내에 특정 키워드가 포함되어 있는지 확인"""
    if text:
        for keyword in keywords:
            if keyword in text:
                return True
    return False

def notice_file_select (download_folder_path):
    """공고 폴더 내 HWP 및 PDF 파일에서 키워드 검색 후 해당 폴더 이동"""
    keyword_file = ''
    # ai_notice_list 폴더 경로 설정
    for file_name in os.listdir(download_folder_path):
        if '과업지시서' in file_name.replace(' ','') or '과업내용서' in file_name.replace(' ',''):
            keyword_file = file_name
        elif '제안요청서' in file_name.replace(' ','') and keyword_file == '':
            keyword_file = file_name 
    return keyword_file

def notice_keyword_search(text):
    ai_keywords = ['AI', '인공지능', 'LLM','생성형','초거대','언어 모델','언어모델','챗봇']
    db_keywords = ['Database', '데이터 레이크', '빅데이터', '데이터 허브','데이터베이스']
    cloud_keywords = ['클라우드','cloud']
    notice_type = []
    if search_keywords_in_text(text, ai_keywords) and '인공지능' not in notice_type:
        notice_type.append('인공지능')
    if search_keywords_in_text(text, db_keywords) and '데이터' not in notice_type:
        notice_type.append('데이터')
    if search_keywords_in_text(text, cloud_keywords) and '클라우드' not in notice_type:
        notice_type.append('클라우드')
    return notice_type


def notice_title_check(notice_title):
    ai_keywords = ['AI', '인공지능', 'LLM','생성형','초거대']
    db_keywords = ['Database', '데이터 레이크', '빅데이터', '데이터 허브','데이터베이스']
    cloud_keywords = ['클라우드','cloud']
    isp_keywords = ['ISP','ISMP']
    """공고 폴더 내 HWP 및 PDF 파일에서 키워드 검색 후 해당 폴더 이동"""
    notice_type = []
    # ai_notice_list 폴더 경로 설정
    if search_keywords_in_text(notice_title, ai_keywords) and '인공지능' not in notice_type:
        notice_type.append('인공지능')
    if search_keywords_in_text(notice_title, db_keywords) and '데이터' not in notice_type:
        notice_type.append('데이터')
    if search_keywords_in_text(notice_title, cloud_keywords) and '클라우드' not in notice_type:
        notice_type.append('클라우드')
    if search_keywords_in_text(notice_title, isp_keywords) and 'ISP/ISMP' not in notice_type:
        notice_type.append('ISP/ISMP')
    return notice_type
