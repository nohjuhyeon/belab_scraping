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
import pandas as pd 
from function_list.g2b_func import notice_file_check, notice_title_check, folder_clear
from datetime import datetime, timedelta

import shutil
def folder_clear(download_folder_path):
    """
    지정된 폴더 내 모든 파일 및 디렉토리를 삭제합니다.

    Args:
        download_folder_path (str): 삭제할 폴더 경로.
    """
    for filename in os.listdir(download_folder_path):
        file_path = os.path.join(download_folder_path, filename)
        try:
            # 파일인지 확인하고 삭제
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 디렉토리 삭제
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


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
        search_start_date = "202504010000"
        search_end_date = "202505010000"
        print(search_start_date)
        print(search_end_date)
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

    # file_url = f"http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoEorderAtchFileInfo?serviceKey={service_key}&pageNo=1&numOfRows=500&inqryDiv=1&inqryBgnDt={search_start_date}&inqryEndDt={search_end_date}&type=json"
    # file_response = requests.get(file_url)
    # file_contents = json.loads(file_response.content)
    # file_items = file_contents["response"]["body"]["items"]
    # file_totalCount = file_contents["response"]["body"]["totalCount"]
    # file_numOfRows = file_contents["response"]["body"]["numOfRows"]
    # file_pages = file_totalCount // file_numOfRows + 1
    # file_elements = []
    # for i in range(file_pages):
    #     file_pagenum = i + 1
    #     file_url = f"http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoEorderAtchFileInfo?serviceKey={service_key}&pageNo={file_pagenum}&numOfRows=500&inqryDiv=1&inqryBgnDt={search_start_date}&inqryEndDt={search_end_date}&type=json"
    #     file_response = requests.get(file_url)
    #     file_contents = json.loads(file_response.content)
    #     file_items = file_contents["response"]["body"]["items"]
    #     file_elements.extend(file_items)

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
        if notice_id in notice_ids and notice_id not in notice_id_list:
            folder_clear(download_folder_path)
            notice_id_list.append(notice_id)
            notice_price = item["presmptPrce"] or 0

            # file_list = []
            # for file_name_num in range(10):
            #     file_name_key = 'ntceSpecFileNm' + str(file_name_num+1)
            #     file_name = item[file_name_key].replace(" ", "")
            #     download_link_key = 'ntceSpecDocUrl'+ str(file_name_num+1)
            #     download_link = item[download_link_key]
            #     if file_name != "" and download_link != "":
            #         file_list.append({'file_name':file_name,'download_link':download_link})    
            # for file_element in file_elements:
            #     if file_element['bidNtceNo'] == bidNtceNo and file_element['eorderAtchFileNm'] != "" and file_element['eorderAtchFileUrl'] != "":
            #         file_list.append({'file_name':file_element['eorderAtchFileNm'],'download_link':file_element['eorderAtchFileUrl']})    
            collection.update_one({'notice_id':notice_id},{"$set":{'price':notice_price}})

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


if __name__ == "__main__":
    collection = mongo_setting("news_scraping", "notice_list")  # MongoDB 설정
    results = collection.find({}, {"_id": 0})  # MongoDB에서 기존 공고 데이터 가져오기
    existing_df = [i for i in results]  # 결과를 리스트로 변환
    existing_df = pd.DataFrame(existing_df)  # DataFrame으로 변환
    # 컬럼 이름 변경 (가독성을 위해 한글로 변경)
    existing_df.rename(
        columns={
            "notice_id": "공고번호",
            "title": "공고명",
            "price": "공고가격(단위: 원)",
            "publishing_agency": "공고 기관",
            "requesting_agency": "수요 기관",
            "start_date": "게시일",
            "end_date": "마감일",
            "open_date":"개찰일",
            "file_list":"파일 목록",
            "link": "링크",
            "type": "비고",
            "notice_class": "공고 유형",
        },
        inplace=True,
    )
    # existing_df = existing_df.loc[existing_df['파일 목록'].isnull()]

    notice_collection(existing_df)