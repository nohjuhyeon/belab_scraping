from selenium.webdriver.common.by import By
import os 
import time
from dotenv import load_dotenv
from function_list.basic_options import selenium_setting,download_path_setting,init_browser
from function_list.g2b_func import notice_check,folder_clear,load_notice_titles_from_json,save_notice_list_to_json
load_dotenv()

def notice_search(search_keyword,notice_list,notice_titles,folder_path):
    chrome_options = selenium_setting()
    chrome_options,download_folder_path = download_path_setting(folder_path,chrome_options)
    browser = init_browser(chrome_options)

    browser.get("https://www.g2b.go.kr:8081/ep/preparation/prestd/preStdSrch.do?preStdRegNo=&referNo=&srchCl=&srchNo=&instCl=2&taskClCd=1&swbizTgYn=&instNm=&dminstCd=&listPageCount=&orderbyItem=1&instSearchRange=&myProdSearchYn=&searchDetailPrdnmNo=&searchDetailPrdnm=&pubYn=Y&taskClCds=A&recordCountPerPage=100")  # - 주소 입력
    time.sleep(1)
    keyword = browser.find_element(by=By.CSS_SELECTOR, value='#prodNm')
    keyword.send_keys(search_keyword)
    click_btn = browser.find_element(by=By.CSS_SELECTOR, value='#frmSearch1 > div.button_wrap > div > a:nth-child(1)')
    click_btn.click()
    time.sleep(3)
    preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(4) > div > a')
    for i in range(len(preparation_elements)):
        folder_clear(download_folder_path)        
        preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(4) > div > a')
        preparation_title = preparation_elements[i].text
        preparation_link = preparation_elements[i].get_attribute('href')
        preparation_link = 'https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo='+preparation_link.split('\'')[1]
        preparation_elements[i].click()
        time.sleep(1)
        preparation_id = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(1) > td:nth-child(4) > div').text
        preparation_price = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(3) > td:nth-child(2) > div').text
        preparation_start_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(4) > td:nth-child(2) > div').text
        if preparation_start_date != '':
            preparation_start_date = preparation_start_date.split(' ')[0]
        preparation_end_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(4) > td:nth-child(4) > div').text
        if preparation_end_date != '':
            preparation_end_date = preparation_end_date.split(' ')[0]
        publishing_agency = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(5) > td > div').text.split('\n')[0]
        requesting_agency = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(6) > td > div').text
        if preparation_title not in notice_titles:
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
        preparation_type = notice_check(download_folder_path)
        dict_preparation = {'id':preparation_id,'title':preparation_title,'price':preparation_price,'publishing_agency':publishing_agency,'requesting_agency':requesting_agency,'start_date':preparation_start_date,'end_date':preparation_end_date,'link':preparation_link,'new':new_preparation,'type':preparation_type}
        notice_list.append(dict_preparation)
        folder_clear(download_folder_path)
        back_btn = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.button_wrap > div > a')
        back_btn.click()
        time.sleep(1)
    browser.quit()
    return notice_list  

def preparation_collection():
    notice_list = []
    # 함수 호출
    folder_path = os.environ.get("folder_path")
    folder_path = 'C:/develops/belab_scraping/'

    notice_titles = load_notice_titles_from_json(folder_path+'preparation_list.json')
    notice_list = preparation_search('isp',notice_list,notice_titles,folder_path)
    notice_list = preparation_search('ismp',notice_list,notice_titles,folder_path)
    json_file_path = os.path.join(folder_path, 'preparation_list.json')
    save_notice_list_to_json(notice_list, json_file_path)
    ai_notice_list = []
    check_list = []
    for notice in notice_list:
        if notice['type'] == 'ai':
            ai_notice_list.append(notice)
        elif notice['type'] == 'check':
            check_list.append(notice)
    time.sleep(1)
    return ai_notice_list,check_list
