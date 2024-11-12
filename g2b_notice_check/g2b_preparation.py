from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os 
import time
import json
from dotenv import load_dotenv

load_dotenv()

def preparation_search(search_keyword,preparation_list,preparation_titles,folder_path):
    # Chrome 브라우저 옵션 생성
    chrome_options = Options()

    # User-Agent 설정
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    # 다운로드 폴더 설정
    download_folder_path = os.path.abspath(folder_path + '/preparation_list')
    if not os.path.exists(download_folder_path):
        os.makedirs(download_folder_path)
    prefs = {
        'download.default_directory': download_folder_path,
        'download.prompt_for_download': False,
        'safebrowsing.enabled': True
    }
    chrome_options.add_experimental_option('prefs', prefs)

    # 추가적인 Chrome 옵션 설정 (특히 Docker 환경에서 필요할 수 있음)
    chrome_options.add_argument('--headless')  # GUI 없는 환경에서 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')  # GPU 사용 안함

    # WebDriver 생성
    webdriver_manager_directory = ChromeDriverManager().install()
    service = ChromeService(webdriver_manager_directory)
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.get("https://www.g2b.go.kr:8081/ep/preparation/prestd/preStdSrch.do?preStdRegNo=&referNo=&srchCl=&srchNo=&instCl=2&taskClCd=1&swbizTgYn=&instNm=&dminstCd=&listPageCount=&orderbyItem=1&instSearchRange=&myProdSearchYn=&searchDetailPrdnmNo=&searchDetailPrdnm=&pubYn=Y&taskClCds=A&recordCountPerPage=100")  # - 주소 입력
    time.sleep(1)
    keyword = browser.find_element(by=By.CSS_SELECTOR, value='#prodNm')
    keyword.send_keys(search_keyword)
    click_btn = browser.find_element(by=By.CSS_SELECTOR, value='#frmSearch1 > div.button_wrap > div > a:nth-child(1)')
    click_btn.click()
    time.sleep(3)
    preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(4) > div > a')
    for i in range(len(preparation_elements)):
        preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(4) > div > a')
        preparation_title = preparation_elements[i].text
        preparation_link = preparation_elements[i].get_attribute('href')
        preparation_link = 'https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo='+preparation_link.split('\'')[1]
        preparation_elements[i].click()
        time.sleep(1)
        preparation_id = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(1) > td:nth-child(2) > div').text
        preparation_price = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(3) > td:nth-child(2) > div').text
        preparation_start_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(4) > td:nth-child(2) > div').text
        if preparation_start_date != '':
            preparation_start_date = preparation_start_date.split(' ')[0]
        preparation_end_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(4) > td:nth-child(4) > div').text
        if preparation_end_date != '':
            preparation_end_date = preparation_end_date.split(' ')[0]
        publishing_agency = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(5) > td > div').text.split('\n')[0]
        requesting_agency = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(6) > td > div').text
        if preparation_title not in preparation_titles:
            new_preparation=True
        else:
            new_preparation=False
        file_list = browser.find_elements(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(8) > td > div > a')
        for j in range(len(file_list)):
            file_list = browser.find_elements(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(8) > td > div > a')
            file_list[j].click()
            time.sleep(3)
        try:
            browser.switch_to.frame('eRfpReqIframe')
            file_list = browser.find_elements(by=By.CSS_SELECTOR,value='span > a')
            for j in range(len(file_list)):
                file_list = browser.find_elements(by=By.CSS_SELECTOR,value='span > a')
                file_list[j].click()
                time.sleep(3)
            browser.switch_to.default_content()
        except:
            pass
        preparation_type = None
        preparation_type = check_list_insert(preparation_type, download_folder_path)
        keywords = ['AI', '인공지능', 'LLM','생성형']
        preparation_type = ai_preparation_list_insert(preparation_type, download_folder_path,keywords)
        dict_preparation = {'preparation_id':preparation_id,'preparation_title':preparation_title,'preparation_price':preparation_price,'publishing_agency':publishing_agency,'requesting_agency':requesting_agency,'preparation_start_date':preparation_start_date,'preparation_end_date':preparation_end_date,'preparation_link':preparation_link,'new_preparation':new_preparation,'preparation_type':preparation_type}
        preparation_list.append(dict_preparation)
        for filename in os.listdir(download_folder_path):
            file_path = os.path.join(download_folder_path, filename)
            try:
                # 파일인지 확인하고 삭제
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

        back_btn = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.button_wrap > div > a')
        back_btn.click()
        time.sleep(1)
    browser.quit()
    return preparation_list

def check_list_insert(preparation_type, download_folder_path):
    # check_list 폴더 경로 설정
    # 공고 폴더들 탐색
    folder_path = os.path.join(download_folder_path)
    
    # 공고 폴더인지 확인 (check_list 폴더는 제외)
    if os.path.isdir(folder_path):
        # 해당 폴더 안의 파일들 탐색
        has_hwp_file = False
        for file_name in os.listdir(folder_path):
            if file_name.lower().endswith('.hwp'):
                has_hwp_file = True
                break            
        # hwp 파일이 없으면 check_list로 이동
        if not has_hwp_file:
            preparation_type = 'check'
    return preparation_type

import os
import shutil
import olefile
import zlib
import struct

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
        return None


def search_keywords_in_hwp(file_name,file_path, keywords):
    """HWP 파일 내에 특정 키워드가 포함되어 있는지 확인"""
    text = get_hwp_text(file_path)
    if text:
        for keyword in keywords:
            if keyword in text:
                print("파일명 : ", file_name)
                print("키워드 : ", keyword)
                return True
    return False

def ai_preparation_list_insert(preparation_type, download_folder_path,keywords):
    """공고 폴더 내 HWP 및 PDF 파일에서 키워드 검색 후 해당 폴더 이동"""
    # ai_notice_list 폴더 경로 설정
    for file_name in os.listdir(download_folder_path):
        file_path = os.path.join(download_folder_path, file_name)
        if file_name.lower().endswith('.hwp'):
            if search_keywords_in_hwp(file_name,file_path, keywords):
                preparation_type = 'ai_preparation'
                time.sleep(1)
                break
    return preparation_type
                    
import json

def load_preparation_titles_from_json(file_path):
    # JSON 파일에서 preparation_title만 추출하여 리스트로 반환
    with open(file_path, 'r', encoding='utf-8') as json_file:
        preparation_list = json.load(json_file)
    
    preparation_titles = [preparation['preparation_title'] for preparation in preparation_list]
    return preparation_titles


import json
import os

def save_preparation_list_to_json(preparation_list, file_path):
    """
    JSON 파일에 공지 목록을 저장합니다. 기존 내용이 있다면 추가합니다.

    Args:
        preparation_list: 저장할 공지 목록 (list)
        file_path: 저장할 JSON 파일 경로 (str)
    """

    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(preparation_list, json_file, ensure_ascii=False, indent=4)


def g2b_preparation_collection():
    preparation_list = []
    # 함수 호출
    folder_path = os.environ.get("folder_path")

    preparation_titles = load_preparation_titles_from_json(folder_path+'preparation_list.json')
    preparation_list = preparation_search('isp',preparation_list,preparation_titles,folder_path)
    preparation_list = preparation_search('ismp',preparation_list,preparation_titles,folder_path)
    json_file_path = os.path.join(folder_path, 'preparation_list.json')
    save_preparation_list_to_json(preparation_list, json_file_path)
    ai_preparation_list = []
    check_list = []
    for notice in preparation_list:
        if notice['preparation_type'] == 'ai_preparation':
            ai_preparation_list.append(notice)
        elif notice['preparation_type'] == 'check':
            check_list.append(notice)
    time.sleep(1)
    return ai_preparation_list,check_list

