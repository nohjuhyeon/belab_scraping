import json
import zipfile
import shutil
import os 
import re
import unicodedata
from function_list.hwp_loader import HWPLoader
from function_list.hwpx_loader import get_hwpx_text
import zipfile

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
    notice_type = None
    for file_name in os.listdir(download_folder_path):
        file_path = os.path.join(download_folder_path, file_name)
        if file_name.lower().endswith('.zip'):
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    for file_info in zip_ref.infolist():
                        # 파일 이름을 CP949로 디코딩 후 UTF-8로 재인코딩
                        decoded_name = file_info.filename.encode('cp437').decode('cp949')
                        file_info.filename = decoded_name  # 파일 이름 수정
                        # 압축 해제할 임시 폴더 경로
                        extract_path = os.path.join(download_folder_path)
                        zip_ref.extract(file_info, extract_path)
                pass
            except:
                pass
    notice_type = check_list_insert(notice_type, download_folder_path)
    notice_type = type_list_insert(notice_type, download_folder_path)
    return notice_type

def check_list_insert(notice_type, download_folder_path):
    # check_list 폴더 경로 설정
    # 공고 폴더들 탐색
    folder_path = os.path.join(download_folder_path)
    
    # 공고 폴더인지 확인 (check_list 폴더는 제외)
    if os.path.isdir(folder_path):
        # 해당 폴더 안의 파일들 탐색
        has_hwp_file = False
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith('.hwp') or file_name.lower().endswith('.hwpx'):
                has_hwp_file = True
                break            
        # hwp 파일이 없으면 check_list로 이동
        if not has_hwp_file:
            notice_type = ['검토 필요']
    return notice_type



def detect_file_type(file_path):
    try:
        with open(file_path, 'rb') as f:
            # 파일의 처음 8바이트 읽기
            header = f.read(8)
            
            # HWP 파일 확인 (OLE2 매직 넘버)
            if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
                loader = HWPLoader(file_path)
                docs = loader.load()

                content = docs[0].page_content
                return content
            
            # HWPX 파일 확인 (ZIP 매직 넘버)
            elif header.startswith(b'\x50\x4B\x03\x04'):
                content,metadata = get_hwpx_text(file_path)
                content = ' '.join(content)
                return content
            
            # 기타 파일
            else:
                return "Unknown"
    except Exception as e:
        return f"Error detecting file type: {e}"


def remove_chinese_characters(s: str):
    """중국어 문자를 제거합니다."""
    return re.sub(r"[\u4e00-\u9fff]+", "", s)

def remove_control_characters(s):
    """깨지는 문자 제거"""
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")

def search_keywords_in_hwp(file_name,file_path, keywords):
    """HWP 파일 내에 특정 키워드가 포함되어 있는지 확인"""
    text = detect_file_type(file_path)
    text = remove_chinese_characters(text)
    text = remove_control_characters(text)
    if text:
        for keyword in keywords:
            if keyword in text:
                # print("파일명 : ", file_name)
                # print("키워드 : ", keyword)
                return True
    return False

def type_list_insert(notice_type, download_folder_path):
    ai_keywords = ['AI', '인공지능', 'LLM','생성형','초거대','언어 모델','언어모델','챗봇']
    db_keywords = ['Database', '데이터 레이크', '빅데이터', '데이터 허브','데이터베이스']
    cloud_keywords = ['클라우드','cloud']
    """공고 폴더 내 HWP 및 PDF 파일에서 키워드 검색 후 해당 폴더 이동"""
    notice_type = []
    # ai_notice_list 폴더 경로 설정
    for file_name in os.listdir(download_folder_path):
        file_path = os.path.join(download_folder_path, file_name)
        if file_name.lower().endswith('.hwp') or file_name.lower().endswith('.hwpx'):
            if search_keywords_in_hwp(file_name,file_path, ai_keywords) and '인공지능' not in notice_type:
                notice_type.append('인공지능')
            if search_keywords_in_hwp(file_name,file_path, db_keywords) and '데이터' not in notice_type:
                notice_type.append('데이터')
            if search_keywords_in_hwp(file_name,file_path, cloud_keywords) and '클라우드' not in notice_type:
                notice_type.append('클라우드')
    return notice_type
                    
def search_keywords_in_title(notice_title, keywords):
    """HWP 파일 내에 특정 키워드가 포함되어 있는지 확인"""
    if notice_title:
        for keyword in keywords:
            if keyword in notice_title:
                return True
    return False

def notice_title_check(notice_title):
    ai_keywords = ['AI', '인공지능', 'LLM','생성형','초거대']
    db_keywords = ['Database', '데이터 레이크', '빅데이터', '데이터 허브','데이터베이스']
    cloud_keywords = ['클라우드','cloud']
    isp_keywords = ['ISP','ISMP']
    """공고 폴더 내 HWP 및 PDF 파일에서 키워드 검색 후 해당 폴더 이동"""
    notice_type = []
    # ai_notice_list 폴더 경로 설정
    if search_keywords_in_title(notice_title, ai_keywords) and '인공지능' not in notice_type:
        notice_type.append('인공지능')
    if search_keywords_in_title(notice_title, db_keywords) and '데이터' not in notice_type:
        notice_type.append('데이터')
    if search_keywords_in_title(notice_title, cloud_keywords) and '클라우드' not in notice_type:
        notice_type.append('클라우드')
    if search_keywords_in_title(notice_title, isp_keywords) and 'ISP/ISMP' not in notice_type:
        notice_type.append('ISP/ISMP')
    return notice_type


def load_notice_titles_from_json(file_path):
    # JSON 파일에서 notice_title만 추출하여 리스트로 반환
    with open(file_path, 'r', encoding='utf-8') as json_file:
        notice_list = json.load(json_file)
    
    notice_titles = [notice['title'] for notice in notice_list]
    return notice_titles

def save_notice_list_to_json(notice_list, file_path):
    """
    JSON 파일에 공지 목록을 저장합니다. 기존 내용이 있다면 추가합니다.

    Args:
        notice_list: 저장할 공지 목록 (list)
        file_path: 저장할 JSON 파일 경로 (str)
    """

    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(notice_list, json_file, ensure_ascii=False, indent=4)
