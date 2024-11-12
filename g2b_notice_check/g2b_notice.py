from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os 
import time
import json
from dotenv import load_dotenv
from datetime import datetime
import zipfile
import xml.etree.ElementTree as ET
import olefile
import zlib
import struct

load_dotenv()

def notice_search(search_keyword,notice_list,notice_titles,folder_path):
    # Chrome 브라우저 옵션 생성
    chrome_options = Options()

    # User-Agent 설정
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    # 다운로드 폴더 설정
    download_folder_path = os.path.abspath(folder_path + '/notice_list')
    if not os.path.exists(download_folder_path):
        os.makedirs(download_folder_path)
    prefs = {
        'download.default_directory': download_folder_path,
        'download.prompt_for_download': False,
        'safebrowsing.enabled': True
    }
    chrome_options.add_experimental_option('prefs', prefs)

    # 추가적인 Chrome 옵션 설정 (특히 Docker 환경에서 필요할 수 있음)
    # chrome_options.add_argument('--headless')  # GUI 없는 환경에서 실행
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--disable-gpu')  # GPU 사용 안함

    # WebDriver 생성
    webdriver_manager_directory = ChromeDriverManager().install()
    service = ChromeService(webdriver_manager_directory)
    browser = webdriver.Chrome(service=service, options=chrome_options)

    browser = webdriver.Chrome(service=ChromeService(webdriver_manager_directory), options=chrome_options)
    browser_url = "https://infose.info21c.net/info21c/bids/list/index?bidtype=ser&bid_suc=bid&division=1&mode=&searchtype=condition&page=1&pageSize=100&bid_kind=&conlevel=&searchWord=&word_type=&sort=-writedt&detailSearch=&search_code%5B%5D=&search_code%5B%5D=&search_code%5B%5D=&search_loc%5B%5D=&search_local%5B%5D=&search_loc%5B%5D=&search_local%5B%5D=&search_loc%5B%5D=&search_local%5B%5D=&date_column=writedt&from_date=2024-10-06&to_date=2024-11-06&price_column=basic&from_price=&to_price=&search_org=&word_column=constnm&word={}&apt_vw=N&sortList=-writedt".format(search_keyword)
    browser.get(browser_url)                                     # - 주소 입력
    time.sleep(1)
    id_input = browser.find_element(by=By.CSS_SELECTOR,value='#id')
    infose_id = os.environ.get("infose_id")
    infose_password = os.environ.get("infose_password")
    infose_id="asog4plp"
    infose_password="dlqckf@01"

    id_input.send_keys(infose_id)
    password_input = browser.find_element(by=By.CSS_SELECTOR,value='#pass')
    password_input.send_keys(infose_password)
    login_btn = browser.find_element(by=By.CSS_SELECTOR,value='#login_btn')
    login_btn.click()
    time.sleep(2)
    search_option = browser.find_element(by=By.CSS_SELECTOR,value='#conditionSearch')
    search_option.click()
    time.sleep(1)
    period_select = browser.find_element(by=By.CSS_SELECTOR,value='#condition_search_form > table > tbody > tr:nth-child(4) > td > div:nth-child(1) > div > button:nth-child(2)')
    period_select.click()
    search_btn = browser.find_element(by=By.CSS_SELECTOR,value='#conditionSearchBtn')
    search_btn.click()
    time.sleep(1)
    
    notice_elements = browser.find_elements(by=By.CSS_SELECTOR,value='#w0 > table > tbody > tr > td:nth-child(2) > a')
    for i in range(len(notice_elements)):
        notice_elements = browser.find_elements(by=By.CSS_SELECTOR,value='#w0 > table > tbody > tr > td:nth-child(2) > a')
        notice_title = notice_elements[i].text
        notice_elements[i].click()
        time.sleep(1)
        notice_id = browser.find_element(by=By.CSS_SELECTOR,value='#basicInfo > table > tbody > tr:nth-child(1) > td:nth-child(4)').text
        notice_price = browser.find_element(by=By.CSS_SELECTOR,value='#basicInfo > table > tbody > tr:nth-child(7) > td:nth-child(4) > b').text
        notice_start_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div > div > div.contents > div.left-content > table > tbody > tr:nth-child(2) > td:nth-child(4)').text
        if notice_start_date != '':
            notice_start_date = datetime.strptime(notice_start_date, "%Y년 %m월 %d일")
            notice_start_date = notice_start_date.strftime("%Y/%m/%d")
        notice_end_date = browser.find_element(by=By.CSS_SELECTOR,value='body > div > div > div.contents > div.left-content > table > tbody > tr:nth-child(4) > td:nth-child(2) > span').text
        if notice_end_date != '':
            notice_end_date = datetime.strptime(notice_end_date, "%Y년 %m월 %d일 %H시 %M분")
            notice_end_date = notice_end_date.strftime("%Y/%m/%d")
        publishing_agency = browser.find_element(by=By.CSS_SELECTOR,value='#basicInfo > table > tbody > tr:nth-child(3) > td:nth-child(4)').text.split('\n')[-1]
        requesting_agency = browser.find_element(by=By.CSS_SELECTOR,value='#basicInfo > table > tbody > tr:nth-child(4) > td:nth-child(2)').text.split('\n')[-1]
        try:
            notice_link = browser.find_element(by=By.CSS_SELECTOR,value='#contentBid > table > tbody > tr:nth-child(2) > td > span:nth-child(2)')
            onclick_text = notice_link.get_attribute("onclick")
            bid_id = onclick_text.split("g2bBidLink('")[1].split("'")[0]
            notice_link = 'https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/menu/frameTgong.do?url=https://www.g2b.go.kr:8101/ep/invitation/publish/bidInfoDtl.do?bidno='+bid_id
        except:
            try:
                notice_link = browser.find_element(by=By.CSS_SELECTOR,value='#contentBid > table > tbody > tr > td > button')
                onclick_attribute = notice_link.get_attribute("onclick")
                # onclick 속성에서 링크 추출
                start_index = onclick_attribute.find("http")
                end_index = onclick_attribute.find("')", start_index)
                notice_link = onclick_attribute[start_index:end_index]
            except:
                notice_link = browser.find_element(by=By.CSS_SELECTOR,value='#contentBid > table > tbody > tr > td > a').get_attribute('href')
            pass
        if notice_title not in notice_titles:
            new_notice=True
        else:
            new_notice=False
        file_list = []
        file_list = browser.find_elements(by=By.CSS_SELECTOR,value='#contentBid > table > tbody > tr:nth-child(1) > td > ul > li > a')
        for j in range(len(file_list)):
            file_list = browser.find_elements(by=By.CSS_SELECTOR,value='#contentBid > table > tbody > tr:nth-child(1) > td > ul > li > a')
            browser.execute_script("arguments[0].scrollIntoView();", file_list[j]) 
            time.sleep(1)
            file_list[j].click()
            time.sleep(2)
        notice_type = None
        for file_name in os.listdir(download_folder_path):
            file_path = os.path.join(download_folder_path, file_name)
            if file_name.lower().endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(download_folder_path)
        notice_type = check_list_insert(notice_type, download_folder_path)
        keywords = ['AI', '인공지능', 'LLM','생성형']
        notice_type = ai_notice_list_insert(notice_type, download_folder_path,keywords)
        dict_notice = {'notice_id':notice_id,'notice_title':notice_title,'notice_price':notice_price,'publishing_agency':publishing_agency,'requesting_agency':requesting_agency,'notice_start_date':notice_start_date,'notice_end_date':notice_end_date,'notice_link':notice_link,'new_notice':new_notice,'notice_type':notice_type}
        notice_list.append(dict_notice)
        for filename in os.listdir(download_folder_path):
            file_path = os.path.join(download_folder_path, filename)
            try:
                # 파일인지 확인하고 삭제
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        back_btn = browser.find_element(by=By.CSS_SELECTOR, value='#top_wrap > div.top_btn > div.top-left_btn.pull-left > span')
        back_btn.click()
        time.sleep(1)
        
    browser.quit()
    return notice_list

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
            notice_type = 'check'
    return notice_type

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

def get_hwpx_text(file_path):
    all_contents = ""  # 모든 파일의 내용을 저장할 변수
    
    with zipfile.ZipFile(file_path, 'r') as zf:
        # 압축 파일 내의 모든 파일 목록을 가져옵니다.
        all_files = zf.namelist()
        
        # 'Contents/' 폴더에 있는 파일들만 필터링합니다.
        contents_files = [file for file in all_files if file.startswith('Contents/')]

        # 각 파일의 내용을 읽어 변수에 저장합니다.
        for file in contents_files:
            with zf.open(file) as f:
                content = f.read()
                try:
                    # 파일 내용을 문자열로 디코딩하고 XML로 파싱하여 읽기 쉽게 변환합니다.
                    xml_content = content.decode('utf-8')
                    root = ET.fromstring(xml_content)
                    
                    # XML 요소를 순회하며 텍스트를 추출합니다.
                    for elem in root.iter():
                        if elem.text:
                            all_contents += elem.text.strip() + " "
                except ET.ParseError:
                    # XML 파싱에 실패한 경우 원본 텍스트를 추가합니다.
                    all_contents += f"Contents of {file} could not be parsed as XML.\n"
                    
    return all_contents

    
def search_keywords(file_name, keywords,text):
    """HWP 파일 내에 특정 키워드가 포함되어 있는지 확인"""
    for keyword in keywords:
        if keyword in text:
            print("파일명 : ", file_name)
            print("키워드 : ", keyword)
            return True
    return False

def ai_notice_list_insert(notice_type, download_folder_path,keywords):
    """공고 폴더 내 HWP 및 PDF 파일에서 키워드 검색 후 해당 폴더 이동"""
    # ai_notice_list 폴더 경로 설정
    for file_name in os.listdir(download_folder_path):
        file_path = os.path.join(download_folder_path, file_name)
        if file_name.lower().endswith('.hwp') :
            text = get_hwp_text(file_path)
            if search_keywords(file_name, keywords,text):
                notice_type = 'ai_notice'
                time.sleep(1)
                break
        elif file_name.lower().endswith('.hwpx'):
            text = get_hwpx_text(file_path)
            if search_keywords(file_name, keywords,text):
                notice_type = 'ai_notice'
                time.sleep(1)
                break
    return notice_type
                    
def load_notice_titles_from_json(file_path):
    # JSON 파일에서 notice_title만 추출하여 리스트로 반환
    with open(file_path, 'r', encoding='utf-8') as json_file:
        notice_list = json.load(json_file)
    
    notice_titles = [notice['notice_title'] for notice in notice_list]
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


def g2b_notice_collection():
    notice_list = []
    # 함수 호출
    folder_path = os.environ.get("folder_path")
    # folder_path = 'C:/develops/belab_scraping/'

    notice_titles = load_notice_titles_from_json(folder_path+'notice_list.json')
    notice_list = notice_search('isp',notice_list,notice_titles,folder_path)
    notice_list = notice_search('ismp',notice_list,notice_titles,folder_path)
    json_file_path = os.path.join(folder_path, 'notice_list.json')
    save_notice_list_to_json(notice_list, json_file_path)
    ai_notice_list = []
    check_list = []
    for notice in notice_list:
        if notice['notice_type'] == 'ai_notice':
            ai_notice_list.append(notice)
        elif notice['notice_type'] == 'check':
            check_list.append(notice)
    time.sleep(1)
    return ai_notice_list,check_list

# g2b_notice_collection()