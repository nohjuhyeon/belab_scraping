from selenium.webdriver.chrome.options import Options
import os 
from pymongo import MongoClient
from dotenv import load_dotenv
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
load_dotenv()
    # 다운로드 폴더 설정
def download_path_setting(folder_path,chrome_options):
    download_folder_path = os.path.abspath(folder_path + '/notice_list')
    if not os.path.exists(download_folder_path):
        os.makedirs(download_folder_path)
    prefs = {
        'download.default_directory': download_folder_path,
        'download.prompt_for_download': False,
        'safebrowsing.enabled': True
    }
    chrome_options.add_experimental_option('prefs', prefs)
    return chrome_options,download_folder_path

def selenium_setting():
    # Chrome 브라우저 옵션 생성
    chrome_options = Options()

    # User-Agent 설정
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    # 추가적인 Chrome 옵션 설정 (특히 Docker 환경에서 필요할 수 있음)
    chrome_options.add_argument('--headless')  # GUI 없는 환경에서 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')  # GPU 사용 안함

    return chrome_options
    # WebDriver 생성
def init_browser(chrome_options):
    webdriver_manager_directory = ChromeDriverManager().install()
    service = ChromeService(webdriver_manager_directory)
    browser = webdriver.Chrome(service=service, options=chrome_options)

    return browser

def mongo_setting(database_name,collection_name):
    mongo_url = os.environ.get("DATABASE_URL")
    mongo_client = MongoClient(mongo_url)
    # database 연결
    database = mongo_client[database_name]
    # collection 작업
    collection = database[collection_name]
    return collection

