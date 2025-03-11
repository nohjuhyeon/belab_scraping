# 데이터명 : 한국주택금융공사_전세자금대출 금리 정보
# from https://www.data.go.kr/data/15129394/openapi.do
import requests 
import json
from selenium.webdriver.common.by import By
import os 
import time
from function_list.basic_options import mongo_setting
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from function_list.basic_options import selenium_setting,download_path_setting,init_browser
from function_list.g2b_func import notice_file_check,notice_title_check,folder_clear
from datetime import datetime, timedelta

folder_path = os.environ.get("folder_path")


chrome_options = selenium_setting()
chrome_options,download_folder_path = download_path_setting(folder_path,chrome_options)
browser = init_browser(chrome_options)
browser.get("https://www.g2b.go.kr/link/PNPE027_01/single/?bidPbancNo=R25BK00688828&bidPbancOrd=000")
# CSS Selector로 모든 <a> 태그 가져오기
time.sleep(3)
WebDriverWait(browser, 10).until(
    EC.invisibility_of_element_located((By.ID, "___processbar2"))  # 로딩 창의 ID를 사용
)
download_elements = browser.find_elements(By.CSS_SELECTOR,value='td>nobr>a')


# 찾은 요소 출력
for element in download_elements:
    if '제안요청서' in element.text.replace(' ','') or '과업지시서' in element.text.replace(' ','') or '과업내용서' in element.text.replace(' ',''):
        element.click()
    # print(element.text)  # <a> 태그의 텍스트
    # print(element.get_attribute("href"))  # href 속성 값
