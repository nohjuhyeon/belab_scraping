from selenium.webdriver.firefox.options import Options
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager  # GeckoDriverManager 사용

load_dotenv()

# 다운로드 폴더 설정
def download_path_setting(folder_path, firefox_options):
    download_folder_path = os.path.abspath(folder_path + '/notice_list')
    if not os.path.exists(download_folder_path):
        os.makedirs(download_folder_path)
    # Firefox에서 다운로드 경로 설정
    firefox_profile = {
        "browser.download.dir": download_folder_path,
        "browser.download.folderList": 2,  # 2: 지정된 경로에 다운로드
        "browser.helperApps.neverAsk.saveToDisk": "application/pdf,application/octet-stream",
        "pdfjs.disabled": True,  # PDF 뷰어 비활성화
    }
    for key, value in firefox_profile.items():
        firefox_options.set_preference(key, value)
    return firefox_options, download_folder_path

# Selenium 설정
def selenium_setting():
    # Firefox 브라우저 옵션 생성
    firefox_options = Options()

    # User-Agent 설정
    firefox_options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
    )

    # 추가적인 Firefox 옵션 설정 (특히 Docker 환경에서 필요할 수 있음)
    firefox_options.add_argument('--headless')  # GUI 없는 환경에서 실행
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-dev-shm-usage')
    firefox_options.add_argument('--disable-gpu')  # GPU 사용 안함 (선택 사항)

    return firefox_options

# WebDriver 생성
def init_browser(firefox_options):
    # GeckoDriverManager를 사용하여 GeckoDriver 설치 및 서비스 설정
    webdriver_manager_directory = GeckoDriverManager().install()
    service = FirefoxService(webdriver_manager_directory)
    browser = webdriver.Firefox(service=service, options=firefox_options)

    return browser

# MongoDB 설정
def mongo_setting(database_name, collection_name):
    mongo_url = os.environ.get("DATABASE_URL")
    mongo_client = MongoClient(mongo_url)
    # database 연결
    database = mongo_client[database_name]
    # collection 작업
    collection = database[collection_name]
    return collection