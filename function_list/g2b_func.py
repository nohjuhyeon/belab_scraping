import time
import json
import zipfile
import shutil
import olefile
import zlib
import struct
import os 
from function_list.hwp_loader import HWPLoader

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
                    # 압축 해제할 임시 폴더 경로
                    extract_path = os.path.join(download_folder_path)
                    zip_ref.extractall(extract_path)
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

import olefile
import zlib
import struct
import zipfile
import xml.etree.ElementTree as ET


def detect_file_type(file_path):
    try:
        with open(file_path, 'rb') as f:
            # 파일의 처음 8바이트 읽기
            header = f.read(8)
            
            # HWP 파일 확인 (OLE2 매직 넘버)
            if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
                content = get_hwp_text(file_path)
                return content
            
            # HWPX 파일 확인 (ZIP 매직 넘버)
            elif header.startswith(b'\x50\x4B\x03\x04'):
                content = get_hwpx_text(file_path)
                return content
            
            # 기타 파일
            else:
                return "Unknown"
    except Exception as e:
        return f"Error detecting file type: {e}"


def get_hwp_text(filename):
    try:
        with olefile.OleFileIO(filename) as f:
            dirs = f.listdir()

            # HWP 파일 검증
            if ["FileHeader"] not in dirs or ["\x05HwpSummaryInformation"] not in dirs:
                print("Not a valid HWP file.")
                return None

            # 문서 포맷 압축 여부 확인
            header = f.openstream("FileHeader")
            header_data = header.read()
            is_compressed = (header_data[36] & 1) == 1

            # Body Sections 불러오기
            nums = []
            for d in dirs:
                if d[0] == "BodyText":
                    nums.append(int(d[1][len("Section"):]))
            sections = ["BodyText/Section" + str(x) for x in sorted(nums)]

            # 전체 text 추출
            text = ""
            for section in sections:
                bodytext = f.openstream(section)
                data = bodytext.read()
                if is_compressed:
                    unpacked_data = zlib.decompress(data, -15)
                else:
                    unpacked_data = data

                # 각 Section 내 text 추출    
                section_text = ""
                i = 0
                size = len(unpacked_data)
                while i < size:
                    header = struct.unpack_from("<I", unpacked_data, i)[0]
                    rec_type = header & 0x3ff
                    rec_len = (header >> 20) & 0xfff

                    if rec_type in [67]:
                        rec_data = unpacked_data[i+4:i+4+rec_len]
                        section_text += rec_data.decode('utf-16', errors='ignore')
                        section_text += "\n"

                    i += 4 + rec_len

                text += section_text
                text += "\n"

            return text
    except Exception as e:
        print(e)
        return None


def get_hwpx_text(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            # Contents 폴더 내의 섹션 파일 목록 찾기
            section_files = [name for name in zf.namelist() if name.startswith('Contents/section') and name.endswith('.xml')]

            # 모든 섹션 파일의 텍스트를 저장할 리스트
            all_texts = []

            for section_file in section_files:
                with zf.open(section_file) as file:
                    tree = ET.parse(file)
                    root = tree.getroot()

                    # 현재 섹션의 텍스트 추출
                    for elem in root.iter():
                        if elem.tag.endswith('t'):  # 텍스트 태그 확인
                            if elem.text:
                                all_texts.append(elem.text.strip())

            # 모든 섹션 텍스트를 하나로 합치기
            return ' '.join(all_texts)
    except Exception as e:
        return f"Error extracting text: {e}"


def search_keywords_in_hwp(file_name,file_path, keywords):
    """HWP 파일 내에 특정 키워드가 포함되어 있는지 확인"""
    # text = detect_file_type(file_path)
    loader = HWPLoader(file_path)
    docs = loader.load()
    text = docs[0].page_content
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
