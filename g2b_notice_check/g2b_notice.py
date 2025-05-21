import requests
import json
from selenium.webdriver.common.by import By
import os
import time
from dotenv import load_dotenv
from function_list.basic_options import mongo_setting
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from function_list.basic_options import (
    selenium_setting,
    download_path_setting,
    init_browser,
)
from function_list.g2b_func import notice_file_check, notice_title_check, folder_clear
from datetime import datetime, timedelta


def wait_for_downloads(download_dir, timeout=30):
    """
    다운로드가 완료될 때까지 기다리는 함수.
    :param download_dir: 다운로드 디렉토리 경로
    :param timeout: 최대 대기 시간 (초)
    :return: 다운로드 완료 여부 (True/False)
    """
    end_time = time.time() + timeout
    while True:
        # 다운로드 디렉토리의 파일 목록 가져오기
        files = os.listdir(download_dir)

        # 임시 파일(.part)이 없는지 확인
        if not any(file.endswith(".part") for file in files):
            return True  # 다운로드 완료

        # 타임아웃 확인
        if time.time() > end_time:
            return False

        # 0.5초 대기 후 다시 확인
        time.sleep(0.5)


def notice_search(notice_list, notice_ids, folder_path):
    """
    공고 데이터를 검색하고 저장하는 함수.

    Args:
        notice_list (List[dict]): 공고 데이터를 저장할 리스트
        notice_ids (List[str]): 기존 공고 ID 리스트 (중복 방지를 위해 사용)
        folder_path (str): 다운로드 폴더의 경로

    Returns:
        notice_list(List[dict]): 업데이트된 공고 리스트
    """

    # MongoDB 컬렉션 설정
    collection = mongo_setting("news_scraping", "notice_list")
    try:
        # 다운로드 폴더 경로 생성
        download_folder_path = os.path.abspath(folder_path + "/notice_list")
        if not os.path.exists(download_folder_path):
            # 폴더가 없으면 생성
            os.makedirs(download_folder_path)  
        # 오늘 날짜와 2일 전 날짜를 가져와서 원하는 형식으로 변환
        search_end_date = datetime.now().strftime("%Y%m%d") + "1159"
        search_start_date = (datetime.now() - timedelta(days=2)).strftime(
            "%Y%m%d"
        ) + "0000"
        service_key = "Qa6CXT4r6qEr%2BkQt%2FJx6wJr5MPx45hKNJwNTScoYryT2uGz7GozIqpjBw%2FRMk1uE8l92NU7h89m20sa%2FXHKuaQ%3D%3D"
        # API 요청 URL 생성
        url = f"http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServcPPSSrch?serviceKey={service_key}&pageNo=1&numOfRows=500&inqryDiv=1&inqryBgnDt={search_start_date}&inqryEndDt={search_end_date}&type=json"

        # API 요청 및 응답 처리
        response = requests.get(url)
        contents = json.loads(response.content)
        items = contents["response"]["body"]["items"]
        totalCount = contents["response"]["body"]["totalCount"]
        numOfRows = contents["response"]["body"]["numOfRows"]
        pages = totalCount // numOfRows + 1

        # 모든 페이지의 데이터를 가져오기
        item_list = []
        for i in range(pages):
            pagenum = i + 1
            url = f"http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServcPPSSrch?serviceKey={service_key}&pageNo={pagenum}&numOfRows=500&inqryDiv=1&inqryBgnDt={search_start_date}&inqryEndDt={search_end_date}&type=json"
            response = requests.get(url)
            contents = json.loads(response.content)
            items = contents["response"]["body"]["items"]
            item_list.extend(items)

        # JSON 파일로 저장
        output_file = "item_list.json"
        try:
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(item_list, file, ensure_ascii=False, indent=4)
            print(f"item_list가 '{output_file}'로 저장되었습니다.")
        except Exception as e:
            print(f"JSON 저장 중 오류 발생: {e}")

    except:
        # JSON 파일 읽기
        file_path = folder_path + "item_list.json"
        print(file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            item_list = json.load(file)

    notice_id_list = []
    item_num = 0
    db_insert_count = 0
    print("총 공고 수 : ", len(item_list))

    # 공고 데이터 처리
    for item in item_list:
        bidNtceNo = item["bidNtceNo"]
        bidNtceOrd = item["bidNtceOrd"]
        notice_id = f"{bidNtceNo}-{bidNtceOrd}"
        item_num += 1

        # 진행 상황 출력
        if item_num % 100 == 0:
            print(item_num)

        # 중복 공고 ID 확인
        if notice_id not in notice_ids and notice_id not in notice_id_list:
            notice_id_list.append(notice_id)
            notice_end_date = item["bidClseDt"]
            notice_start_date = item["rgstDt"]
            notice_title = item["bidNtceNm"]
            notice_link = item["bidNtceDtlUrl"]
            requesting_agency = item["dminsttNm"]
            publishing_agency = item["ntceInsttNm"]
            notice_price = item["asignBdgtAmt"] or "0 원"
            for file_name_num in range(10):
                file_name_key = 'ntceSpecFileNm' + str(file_name_num+1)
                file_name = item[file_name_key].replace(" ", "")
                if "제안요청서" in file_name or "과업요청서" in file_name or "과업내용서" in file_name:
                    download_link_key = 'ntceSpecDocUrl'+ str(file_name_num+1)
                    download_link = item[download_link_key]
                    file_path = os.path.join(download_folder_path, file_name)

                    try:
                        response = requests.get(download_link, stream=True)
                        response.raise_for_status()  # HTTP 에러가 발생하면 예외를 발생시킴
                        with open(file_path, 'wb') as file:
                            for chunk in response.iter_content(chunk_size=8192):  # 대용량 파일 처리
                                file.write(chunk)
                        wait_for_downloads(download_folder_path)
                        print(f"파일이 성공적으로 다운로드되었습니다: {file_name}")
                    except requests.exceptions.RequestException as e:
                        print(f"파일 다운로드 중 오류가 발생했습니다: {e}")
                file_url = f"http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoEorderAtchFileInfo?serviceKey={service_key}&pageNo={pagenum}&numOfRows=500&inqryDiv=1&inqryBgnDt={search_start_date}&inqryEndDt={search_end_date}&bidNtceNo={bidNtceNo}&type=json"
                file_response = requests.get(file_url)
                file_contents = json.loads(file_response.content)
                file_items = file_contents["response"]["body"]["items"]
                for file_item in file_items:
                    if file_item['bidNtceNo'] == bidNtceNo:
                        pass
                try:
                    # 파일 내용 확인 및 분류
                    it_notice_check,file_keywords,category_dict,category_list,summary,context = notice_file_check(download_folder_path)
                    notice_type = notice_title_check(notice_title)
                    for j in file_keywords:
                        if j not in notice_type:
                            notice_type.append(j)
                    for j in category_list:
                        if j not in notice_type:
                            notice_type.append(j)
                    notice_type = ", ".join(notice_type)
                    folder_clear(download_folder_path)
                    time.sleep(1)

                    # 공고 데이터를 MongoDB에 저장
                    dict_notice = {
                        "notice_id": notice_id,
                        "title": notice_title,
                        "price": notice_price,
                        "publishing_agency": publishing_agency,
                        "requesting_agency": requesting_agency,
                        "start_date": notice_start_date,
                        "end_date": notice_end_date,
                        "link": notice_link,
                        "it_notice_check": it_notice_check,
                        "summary": summary,
                        "type": notice_type,
                        "notice_class": "입찰 공고",
                        # 'notice_content':context
                    }
                    notice_list.append(dict_notice)
                    collection.insert_one(dict_notice)
                    db_insert_count += 1
                    break
                except Exception as e:
                    time.sleep(2)
    print("저장한 공고 수:", db_insert_count)
    return notice_list


def notice_collection(existing_df):
    """
    기존 공고 데이터를 기반으로 새로운 공고를 수집합니다.

    Args:
        existing_df (DataFrame): 기존 공고 데이터가 포함된 데이터프레임

    Returns:
        notice_list(List[dict]): 업데이트된 공고 리스트
    """
    notice_list = []
    notice_ids = existing_df.loc[
        existing_df["공고 유형"] == "입찰 공고", "공고번호"
    ].to_list()
    load_dotenv(dotenv_path='/app/belab_scraping/.env')
    folder_path = os.environ.get("folder_path")
    notice_list = notice_search(notice_list, notice_ids, folder_path)
    return notice_list
