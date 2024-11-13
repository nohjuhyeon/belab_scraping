from selenium.webdriver.common.by import By
import os 
import time
from dotenv import load_dotenv
from function_list.basic_options import selenium_setting,download_path_setting,init_browser
from function_list.g2b_func import notice_check,folder_clear,load_notice_titles_from_json,save_notice_list_to_json
from datetime import datetime
load_dotenv()

def notice_search(search_keyword,notice_list,notice_titles,folder_path):
    chrome_options = selenium_setting()
    chrome_options,download_folder_path = download_path_setting(folder_path,chrome_options)
    browser = init_browser(chrome_options)
    browser_url = "https://infose.info21c.net/info21c/bids/list/index?bidtype=ser&bid_suc=bid&division=1&mode=&searchtype=condition&page=1&pageSize=100&bid_kind=&conlevel=&searchWord=&word_type=&sort=-writedt&detailSearch=&search_code%5B%5D=&search_code%5B%5D=&search_code%5B%5D=&search_loc%5B%5D=&search_local%5B%5D=&search_loc%5B%5D=&search_local%5B%5D=&search_loc%5B%5D=&search_local%5B%5D=&date_column=writedt&from_date=2024-10-06&to_date=2024-11-06&price_column=basic&from_price=&to_price=&search_org=&word_column=constnm&word={}&apt_vw=N&sortList=-writedt".format(search_keyword)
    browser.get(browser_url)                                     # - 주소 입력
    time.sleep(1)
    id_input = browser.find_element(by=By.CSS_SELECTOR,value='#id')
    infose_id = os.environ.get("infose_id")
    infose_password = os.environ.get("infose_password")

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
        folder_clear(download_folder_path)
        notice_elements = browser.find_elements(by=By.CSS_SELECTOR,value='#w0 > table > tbody > tr > td:nth-child(2) > a')
        notice_title = notice_elements[i].text
        notice_elements[i].click()
        time.sleep(1)
        notice_id = browser.find_element(by=By.CSS_SELECTOR,value='#basicInfo > table > tbody > tr:nth-child(1) > td:nth-child(4)').text
        notice_price = browser.find_element(by=By.CSS_SELECTOR,value='#basicInfo > table > tbody > tr:nth-child(7) > td:nth-child(4) > b').text
        notice_price = notice_price.replace('₩', '').replace('(조달수수료 포함)', '').replace('원', '').replace(' ', '')
        if notice_price != '':
            notice_price = notice_price + ' 원'
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
            try:
                bid_id = notice_link.get_attribute("onclick").split("g2bBidLink('")[1].split("'")[0]
                notice_link = 'https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/menu/frameTgong.do?url=https://www.g2b.go.kr:8101/ep/invitation/publish/bidInfoDtl.do?bidno='+bid_id
            except:
                bid_id = notice_link.get_attribute("onclick").split("?")[-1].split("&")[0]
                notice_link = 'https://www.g2b.go.kr/pt/menu/selectSubFrame.do?framesrc=/pt/menu/frameTgong.do?url=https://www.g2b.go.kr:8101/ep/invitation/publish/bidInfoDtl.do?'+bid_id
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
        notice_type = notice_check(download_folder_path)
        dict_notice = {'id':notice_id,'title':notice_title,'price':notice_price,'publishing_agency':publishing_agency,'requesting_agency':requesting_agency,'start_date':notice_start_date,'end_date':notice_end_date,'link':notice_link,'new':new_notice,'type':notice_type}
        notice_list.append(dict_notice)
        folder_clear(download_folder_path)
        back_btn = browser.find_element(by=By.CSS_SELECTOR, value='#top_wrap > div.top_btn > div.top-left_btn.pull-left > span')
        back_btn.click()
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
        if notice['type'] == 'ai':
            ai_notice_list.append(notice)
        elif notice['type'] == 'check':
            check_list.append(notice)
    time.sleep(1)
    return ai_notice_list,check_list
