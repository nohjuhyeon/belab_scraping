from selenium.webdriver.common.by import By
import os 
import time
from function_list.basic_options import mongo_setting
from datetime import datetime, timedelta
from function_list.basic_options import selenium_setting, download_path_setting, init_browser
from function_list.g2b_func import notice_file_check, notice_title_check, folder_clear


def preparation_search(notice_list, notice_ids, folder_path):
    """
    사전 규격 데이터를 검색하고 수집하는 함수.

    Args:
        notice_list(List[dict]): 공고 데이터를 저장할 리스트
        notice_ids(List[str]): 기존 공고 ID 리스트 (중복 방지를 위해 사용)
        folder_path (str): 다운로드 폴더의 경로

    Returns:
        notice_list(List[dict]): 업데이트된 공고 리스트
    """

    # Selenium 설정 및 브라우저 초기화
    chrome_options = selenium_setting()
    chrome_options, download_folder_path = download_path_setting(folder_path, chrome_options)
    browser = init_browser(chrome_options)

    # G2B 사전 규격 검색 페이지 접속
    browser.get("https://www.g2b.go.kr:8081/ep/preparation/prestd/preStdSrch.do?preStdRegNo=&referNo=&srchCl=&srchNo=&instCl=2&taskClCd=1&prodNm=&swbizTgYn=&instNm=&dminstCd=&listPageCount=&orderbyItem=1&instSearchRange=&myProdSearchYn=&searchDetailPrdnmNo=&searchDetailPrdnm=&pubYn=Y&taskClCds=5&recordCountPerPage=100")
    time.sleep(1)

    # 검색 기간 설정 (오늘 날짜와 2일 전 날짜)
    end_date = browser.find_element(by=By.CSS_SELECTOR, value='#toRcptDt')
    end_date.clear()
    today_date = datetime.now().strftime("%Y/%m/%d")
    end_date.send_keys(today_date)

    seven_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y/%m/%d")
    start_date = browser.find_element(by=By.CSS_SELECTOR, value='#fromRcptDt')
    start_date.clear()
    start_date.send_keys(seven_days_ago)

    # 검색 버튼 클릭
    click_btn = browser.find_element(by=By.CSS_SELECTOR, value='#frmSearch1 > div.button_wrap > div > a:nth-child(1)')
    click_btn.click()
    time.sleep(3)

    # 공고 링크 리스트 초기화
    page_num = 1
    link_list = []
    preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(4) > div > a')
    preparation_elements[0].click()
    time.sleep(1)
    back_btn = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.button_wrap > div > a')
    back_btn.click()
    time.sleep(1)
    current_page = browser.current_url

    # 페이지를 순회하며 공고 링크 수집
    while True:
        preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(2) > div > a')
        if len(preparation_elements) == 0:
            break
        else:
            for preparation_element in preparation_elements:
                preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(2) > div > a')
                preparation_id = preparation_element.text
                if preparation_id not in notice_ids:
                    preparation_link = preparation_element.get_attribute('href')
                    link_list.append(preparation_link)
            page_num += 1
            new_page_num = '&currentPageNo=' + str(page_num)
            new_page = current_page + new_page_num
            browser.get(new_page)

    print("새로 올라온 사전 규격: ", len(link_list))

    # 수집한 링크를 순회하며 공고 상세 정보 수집
    for k in range(len(link_list)):
        preparation_link = link_list[k]
        folder_clear(download_folder_path)        
        preparation_link = 'https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo=' + preparation_link.split('\'')[1]
        browser.get(preparation_link)
        time.sleep(1)

        # 공고 정보 초기화
        preparation_id = ''
        preparation_title = ''
        preparation_price = ''
        preparation_start_date = ''
        requesting_agency = ''
        publishing_agency = ''
        preparation_end_date = ''

        # 공고 상세 정보 추출
        preparation_id = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.section > table > tbody > tr:nth-child(1) > td:nth-child(4) > div').text
        preparation_title = browser.find_element(by=By.CSS_SELECTOR, value='.table_info > tbody:nth-child(3) > tr:nth-child(2) > td:nth-child(2) > div:nth-child(1)').text
        preparation_price = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.section > table > tbody > tr:nth-child(3) > td:nth-child(2) > div').text
        preparation_price = preparation_price.replace('₩', '').replace('(조달수수료 포함)', '').replace('원', '').replace(' ', '')
        if preparation_price != '':
            preparation_price = preparation_price + ' 원'

        preparation_start_date = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.section > table > tbody > tr:nth-child(4) > td:nth-child(2) > div').text
        if preparation_start_date != '':
            preparation_start_date = preparation_start_date.split(' ')[0]
        preparation_end_date = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.section > table > tbody > tr:nth-child(4) > td:nth-child(4) > div').text
        if preparation_end_date != '':
            preparation_end_date = preparation_end_date.split(' ')[0]
        publishing_agency = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.section > table > tbody > tr:nth-child(5) > td > div').text.split('\n')[0]
        requesting_agency = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.section > table > tbody > tr:nth-child(6) > td > div').text

        # 첨부 파일 다운로드
        file_list = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div.section > table > tbody > tr:nth-child(8) > td > div > a')
        for j in range(len(file_list)):
            file_list = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div.section > table > tbody > tr:nth-child(8) > td > div > a')
            file_list[j].click()
            time.sleep(3)

        try:
            browser.switch_to.frame('eRfpReqIframe')
            file_list = browser.find_elements(by=By.CSS_SELECTOR, value='span > a')
            for j in range(len(file_list)):
                file_list = browser.find_elements(by=By.CSS_SELECTOR, value='span > a')
                file_list[j].click()
            browser.switch_to.default_content()
        except:
            pass

        # 공고 유형 분석
        preparation_type = []
        file_keywords = notice_file_check(download_folder_path)
        preparation_type = notice_title_check(preparation_title)
        for j in file_keywords:
            if j not in preparation_type:
                preparation_type.append(j)
        preparation_type = ', '.join(preparation_type)

        # 공고 데이터 저장
        dict_preparation = {
            'notice_id': preparation_id,
            'title': preparation_title,
            'price': preparation_price,
            'publishing_agency': publishing_agency,
            'requesting_agency': requesting_agency,
            'start_date': preparation_start_date,
            'end_date': preparation_end_date,
            'link': preparation_link,
            'type': preparation_type,
            'notice_class': '사전 규격'
        }
        notice_list.append(dict_preparation)
        folder_clear(download_folder_path)

    browser.quit()
    return notice_list  


def preparation_collection(existing_df):
    """
    기존 데이터를 기반으로 새로운 사전 규격 공고를 수집합니다.

    Args:
        existing_df (DataFrame): 기존 공고 데이터가 포함된 데이터프레임

    Returns:
        notice_list(List[dict]): 업데이트된 공고 리스트
    """
    notice_list = []
    collection = mongo_setting('news_scraping', 'notice_list')
    notice_ids = existing_df.loc[existing_df['공고 유형'] == '사전 규격', '공고번호'].to_list()
    folder_path = os.environ.get("folder_path")

    # 사전 규격 검색 및 수집
    notice_list = preparation_search(notice_list, notice_ids, folder_path)
    if len(notice_list) > 0:
        collection.insert_many(notice_list)

    return notice_list
