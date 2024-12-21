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

    browser.get("https://www.g2b.go.kr:8081/ep/tbid/tbidFwd.do?area=&areaNm=&bidNm=&recordCountPerPage=100")  # - 주소 입력
    time.sleep(1)
    keyword = browser.find_element(by=By.CSS_SELECTOR, value='#bidNm')
    keyword
    keyword.send_keys(search_keyword)
    date_btn = browser.find_element(by=By.CSS_SELECTOR,value='#setMonth1_2')
    date_btn.click()
    notice_type = browser.find_element(by=By.CSS_SELECTOR,value='#taskClCds5')
    notice_type.click()
    list_count_box = browser.find_element(by=By.CSS_SELECTOR,value='#recordCountPerPage')
    list_count_box.click()
    count_100 = browser.find_element(by=By.CSS_SELECTOR,value='#recordCountPerPage > option:nth-child(5)')
    count_100.click()
    click_btn = browser.find_element(by=By.CSS_SELECTOR, value='#buttonwrap > div > a:nth-child(1)')
    click_btn.click()
    time.sleep(3)
    main_page = browser.current_url
    notice_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#resultForm > div.results > table > tbody > tr > td:nth-child(4) > div > a')
    for i in range(len(notice_elements)):
        folder_clear(download_folder_path)    
        browser.get(main_page)    
        notice_elements = browser.find_elements(by=By.CSS_SELECTOR, value='#resultForm > div.results > table > tbody > tr > td:nth-child(4) > div > a')
        notice_title = notice_elements[i].text
        if 'ISP' in notice_title or 'ISMP' in notice_title:
            
            notice_link = notice_elements[i].get_attribute('href')
            notice_elements[i].click()
            time.sleep(1)
            try:
                click_btn = browser.find_element(by=By.CSS_SELECTOR,value='#epDialogBtns > a')
                click_btn.click()
                time.sleep(1)
            except:
                pass
            notice_info_title = browser.find_elements(by=By.CSS_SELECTOR,value='div.section > table >tbody > tr > th')
            notice_info_content = browser.find_elements(by=By.CSS_SELECTOR,value='div.section > table >tbody > tr > td')
            for i in range(len(notice_info_title)):
                if notice_info_title[i].text == '게시일시':
                    notice_start_date = notice_info_content[i].text
                    if notice_start_date != '':
                        notice_start_date = notice_start_date.split(' ')[0]
                elif notice_info_title[i].text == '입찰마감일시':
                    notice_end_date = notice_info_content[i].text
                    if notice_end_date != '':
                        notice_end_date = notice_end_date.split(' ')[0]
                elif notice_info_title[i].text == '입찰공고번호':
                    notice_id = notice_info_content[i].text
                elif '사업금액' in notice_info_title[i].text :
                    notice_price = notice_info_content[i].text
                    notice_price = notice_price.replace('₩', '').replace('(조달수수료 포함)', '').replace('원', '').replace(' ', '')
                    if notice_price != '':
                        notice_price = notice_price + ' 원'
                elif notice_info_title[i].text == '입찰공고번호':
                    notice_id = notice_info_content[i].text
                elif notice_info_title[i].text == '수요기관':
                    requesting_agency = notice_info_content[i].text
                elif notice_info_title[i].text == '공고기관':
                    publishing_agency = notice_info_content[i].text
            if notice_title not in notice_titles:
                new_notice=True
            else:
                new_notice=False
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
                        time.sleep(3)
            notice_type = notice_check(download_folder_path)
            dict_notice = {'notice_id':notice_id,'title':notice_title,'price':notice_price,'publishing_agency':publishing_agency,'requesting_agency':requesting_agency,'start_date':notice_start_date,'end_date':notice_end_date,'link':notice_link,'new':new_notice,'type':notice_type}
            notice_list.append(dict_notice)
            print(dict_notice)
            folder_clear(download_folder_path)
            time.sleep(1)
    browser.quit()
    return notice_list  

def notice_collection():
    notice_list = []
    # 함수 호출

    folder_path = os.environ.get("folder_path")

    notice_titles = load_notice_titles_from_json(folder_path+'g2b_data/notice_list.json')
    
    notice_list = notice_search('isp',notice_list,notice_titles,folder_path)
    notice_list = notice_search('ismp',notice_list,notice_titles,folder_path)
    json_file_path = os.path.join(folder_path, 'g2b_data/notice_list.json')
    save_notice_list_to_json(notice_list, json_file_path)
    ai_notice_list = []
    check_list = []
    for notice in notice_list:
        if '인공지능' in notice['type'] :
            ai_notice_list.append(notice)
        if '데이터베이스' in notice['type']:
            ai_notice_list.append(notice)
        if '검토 필요' in notice['type']:
            check_list.append(notice)
    time.sleep(1)
    return ai_notice_list,check_list
# notice_collection()