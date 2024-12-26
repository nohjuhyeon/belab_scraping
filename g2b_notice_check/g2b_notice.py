from selenium.webdriver.common.by import By
import os 
import time
from function_list.basic_options import mongo_setting
from datetime import datetime, timedelta


from dotenv import load_dotenv
from function_list.basic_options import selenium_setting,download_path_setting,init_browser
from function_list.g2b_func import notice_file_check,notice_title_check,folder_clear
load_dotenv()

def notice_search(search_keyword,notice_list,notice_links,folder_path):
    collection = mongo_setting('news_scraping','new_notice_list')
    chrome_options = selenium_setting()
    chrome_options,download_folder_path = download_path_setting(folder_path,chrome_options)
    browser = init_browser(chrome_options)

    browser.get("https://www.g2b.go.kr:8081/ep/tbid/tbidFwd.do?area=&areaNm=&bidNm=&recordCountPerPage=100&taskClCds=5")  # - 주소 입력
    time.sleep(1)
    
    end_date = browser.find_element(by=By.CSS_SELECTOR,value='#toBidDt')
    end_date.clear()
    today_date = datetime.now().strftime("%Y/%m/%d")
    end_date.send_keys(today_date)
    
    seven_days_ago = datetime.now() - timedelta(days=3)
    seven_days_ago = seven_days_ago.strftime("%Y/%m/%d")
    start_date = browser.find_element(by=By.CSS_SELECTOR,value='#fromBidDt')
    start_date.clear()
    start_date.send_keys(seven_days_ago)
    
    list_count_box = browser.find_element(by=By.CSS_SELECTOR,value='#recordCountPerPage')
    list_count_box.click()
    count_100 = browser.find_element(by=By.CSS_SELECTOR,value='#recordCountPerPage > option:nth-child(5)')
    count_100.click()
    click_btn = browser.find_element(by=By.CSS_SELECTOR, value='#buttonwrap > div > a:nth-child(1)')
    click_btn.click()
    time.sleep(3)
    link_list = []
    while True:
        try:
            notice_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#resultForm > div.results > table > tbody > tr > td:nth-child(4) > div > a')
            for notice_element in notice_elements:
                notice_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#resultForm > div.results > table > tbody > tr > td:nth-child(4) > div > a')
                notice_link = notice_element.get_attribute('href')
                if notice_link not in notice_links:
                    link_list.append(notice_link)
            next_page = browser.find_element(by=By.CSS_SELECTOR,value='#pagination > a.default')
            next_page.click()
        except:
            break
    print(len(link_list))
    for k in range(len(link_list)):
        print(k)
        notice_link = link_list[k]
        folder_clear(download_folder_path)    
        browser.get(notice_link)    
        try:
            click_btn = browser.find_element(by=By.CSS_SELECTOR,value='#epDialogBtns > a')
            click_btn.click()
            time.sleep(1)
        except:
            pass
        notice_info_title = browser.find_elements(by=By.CSS_SELECTOR,value='div.section > table >tbody > tr > th')
        notice_info_content = browser.find_elements(by=By.CSS_SELECTOR,value='div.section > table >tbody > tr > td')
        notice_title = ''
        notice_start_date = ''
        notice_end_date = ''
        notice_price =''
        requesting_agency = ''
        publishing_agency = ''
        notice_id = ''
        for j in range(len(notice_info_title)):
            if '공고명' in notice_info_title[j].text:
                notice_title = notice_info_content[j].text
            if '공고일시' in notice_info_title[j].text :
                notice_start_date = notice_info_content[j].text
                if notice_start_date != '':
                    notice_start_date = notice_start_date.split(' ')[0]
            if '입찰서접수 마감일시' in notice_info_title[j].text or '입찰마감일시' in notice_info_title[j].text:
                notice_end_date = notice_info_content[j].text
                if notice_end_date != '':
                    notice_end_date = notice_end_date.split(' ')[0]
            if '입찰공고번호' in notice_info_title[j].text :
                notice_id = notice_info_content[j].text
            if '추정가격' in notice_info_title[j].text and notice_price == '':
                notice_price = notice_info_content[j].text
                notice_price = notice_price.replace('₩', '').replace('(조달수수료 포함)', '').replace('원', '').replace(' ', '')
                if notice_price != '':
                    notice_price = notice_price + ' 원'
            if '사업금액' in notice_info_title[j].text :
                notice_price = notice_info_content[j].text
                notice_price = notice_price.replace('₩', '').replace('(조달수수료 포함)', '').replace('원', '').replace(' ', '')
                if notice_price != '':
                    notice_price = notice_price + ' 원'
            if notice_info_title[j].text == '수요기관':
                requesting_agency = notice_info_content[j].text
            if notice_info_title[j].text == '공고기관':
                publishing_agency = notice_info_content[j].text
        file_block = browser.find_elements(by=By.CSS_SELECTOR,value='div.results')
        for j in range(len(file_block)):
            file_block = browser.find_elements(by=By.CSS_SELECTOR,value='div.results')
            file_list = file_block[j].find_elements(by=By.CSS_SELECTOR,value='a')
            if len(file_list) != 0:
                for file_element in file_list:
                    if '.hwp' in file_element.text or '.pdf' in file_element.text or '.doc' in file_element.text: 
                        try:
                            file_element.click()
                        except:
                            pass
        file_keywords = notice_file_check(download_folder_path)
        notice_type = notice_title_check(notice_title)
        for j in file_keywords:
            if j not in notice_type:
                notice_type.append(j)                
        notice_type = ', '.join(notice_type)
        dict_notice = {'notice_id':notice_id,'title':notice_title,'price':notice_price,'publishing_agency':publishing_agency,'requesting_agency':requesting_agency,'start_date':notice_start_date,'end_date':notice_end_date,'link':notice_link,'type':notice_type,'notice_class':'입찰 공고'}
        # collection.insert_one(dict_notice)
        notice_list.append(dict_notice)
        # print(dict_notice)
        folder_clear(download_folder_path)
        time.sleep(1)
    browser.quit()
    return notice_list  

def notice_collection(existing_df):
    notice_list = []
    # 함수 호출
    # collection = mongo_setting('news_scraping','new_notice_list')
    # results = collection.find({},{'_id':0,'link':1})
    # notice_links = [i['link'] for i in results]
    notice_links = existing_df.loc[existing_df['공고 유형']=='입찰 공고','링크'].to_list()
    folder_path = os.environ.get("folder_path")

    notice_list = notice_search('ISP',notice_list,notice_links,folder_path)
    # notice_list = notice_search('ISMP',notice_list,notice_titles,folder_path)
    # if len(notice_list)> 0:
    #     collection.insert_many(notice_list)

    return notice_list