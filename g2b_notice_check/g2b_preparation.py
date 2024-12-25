from selenium.webdriver.common.by import By
import os 
import time
from function_list.basic_options import mongo_setting
from datetime import datetime, timedelta

from dotenv import load_dotenv
from function_list.basic_options import selenium_setting,download_path_setting,init_browser
from function_list.g2b_func import notice_file_check,notice_title_check,folder_clear
load_dotenv()

def preparation_search(search_keyword,notice_list,notice_ids,folder_path):
    collection = mongo_setting('news_scraping','new_notice_list')
    chrome_options = selenium_setting()
    chrome_options,download_folder_path = download_path_setting(folder_path,chrome_options)
    browser = init_browser(chrome_options)

    browser.get("https://www.g2b.go.kr:8081/ep/preparation/prestd/preStdSrch.do?preStdRegNo=&referNo=&srchCl=&srchNo=&instCl=2&taskClCd=1&prodNm=&swbizTgYn=&instNm=&dminstCd=&listPageCount=&orderbyItem=1&instSearchRange=&myProdSearchYn=&searchDetailPrdnmNo=&searchDetailPrdnm=&pubYn=Y&taskClCds=5&recordCountPerPage=100")  # - 주소 입력
    time.sleep(1)
    end_date = browser.find_element(by=By.CSS_SELECTOR,value='#toRcptDt')
    end_date.clear()
    today_date = datetime.now().strftime("%Y/%m/%d")
    end_date.send_keys(today_date)
    
    seven_days_ago = datetime.now() - timedelta(days=2)
    seven_days_ago = seven_days_ago.strftime("%Y/%m/%d")
    start_date = browser.find_element(by=By.CSS_SELECTOR,value='#fromRcptDt')
    start_date.clear()
    start_date.send_keys(seven_days_ago)


    click_btn = browser.find_element(by=By.CSS_SELECTOR, value='#frmSearch1 > div.button_wrap > div > a:nth-child(1)')
    click_btn.click()
    time.sleep(3)
    page_num = 1
    link_list = []
    preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(4) > div > a')
    preparation_elements[0].click()
    time.sleep(1)
    back_btn = browser.find_element(by=By.CSS_SELECTOR, value='#container > div.button_wrap > div > a')
    back_btn.click()
    time.sleep(1)
    current_page = browser.current_url
    while True:
        preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(2) > div > a')
        if len(preparation_elements)==0:
            break
        else:
            for preparation_element in preparation_elements:
                preparation_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#container > div > table > tbody > tr > td:nth-child(2) > div > a')
                preparation_id = preparation_element.text
                if preparation_id not in notice_ids:
                    preparation_link = preparation_element.get_attribute('href')
                    link_list.append(preparation_link)
            page_num += 1
            new_page_num = '&currentPageNo='+str(page_num)
            new_page = current_page + new_page_num
            browser.get(new_page)


    for k in range(len(link_list)):
        preparation_link = link_list[k]
        folder_clear(download_folder_path)        
        preparation_link = 'https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo='+preparation_link.split('\'')[1]
        browser.get(preparation_link)
        time.sleep(1)
        preparation_id = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(1) > td:nth-child(4) > div').text
        preparation_title = browser.find_element(by=By.CSS_SELECTOR,value='.table_info > tbody:nth-child(3) > tr:nth-child(2) > td:nth-child(2) > div:nth-child(1)').text
        preparation_price = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(3) > td:nth-child(2) > div').text
        preparation_price = preparation_price.replace('₩', '').replace('(조달수수료 포함)', '').replace('원', '').replace(' ', '')
        if preparation_price != '':
            preparation_price = preparation_price + ' 원'

        preparation_start_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(4) > td:nth-child(2) > div').text
        if preparation_start_date != '':
            preparation_start_date = preparation_start_date.split(' ')[0]
        preparation_end_date = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(4) > td:nth-child(4) > div').text
        if preparation_end_date != '':
            preparation_end_date = preparation_end_date.split(' ')[0]
        publishing_agency = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(5) > td > div').text.split('\n')[0]
        requesting_agency = browser.find_element(by=By.CSS_SELECTOR,value='#container > div.section > table > tbody > tr:nth-child(6) > td > div').text
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
            browser.switch_to.default_content()
        except:
            pass
        preparation_type = []

        file_keywords = notice_file_check(download_folder_path)
        preparation_type = notice_title_check(preparation_title)
        for j in file_keywords:
            if j not in preparation_type:
                preparation_type.append(j)
        preparation_type = ', '.join(preparation_type)

        dict_preparation = {'notice_id':preparation_id,'title':preparation_title,'price':preparation_price,'publishing_agency':publishing_agency,'requesting_agency':requesting_agency,'start_date':preparation_start_date,'end_date':preparation_end_date,'link':preparation_link,'type':preparation_type,'notice_class':'사전 규격'}
        collection.insert_one(dict_preparation)
        notice_list.append(dict_preparation)
        folder_clear(download_folder_path)
    browser.quit()
    return notice_list  

def preparation_collection():
    notice_list = []
    notice_list = []
    # 함수 호출
    collection = mongo_setting('news_scraping','new_notice_list')
    results = collection.find({},{'_id':0,'notice_id':1})
    notice_ids = [i['notice_id'] for i in results]

    folder_path = os.environ.get("folder_path")

    notice_list = preparation_search('ISP',notice_list,notice_ids,folder_path)
    # notice_list = preparation_search('ISMP',notice_list,notice_titles,folder_path)
    # notice_list = preparation_search('인공지능',notice_list,notice_titles,folder_path)
    # notice_list = preparation_search('데이터베이스',notice_list,notice_titles,folder_path)
    # if len(notice_list)> 0:
    #     collection.insert_many(notice_list)

