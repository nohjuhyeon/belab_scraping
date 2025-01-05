import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import numpy as np
from datetime import datetime, timedelta
import os 
from function_list.basic_options import mongo_setting
from pymongo import MongoClient
import pandas as pd

def google_sheet_add(notice_type, df,spreadsheet_url):
    # OAuth2 인증을 위한 서비스 계정 키 파일 경로
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # 개인에 따라 수정 필요 - 다운로드 받았던 키 값 경로
    json_key_str = os.environ.get("google_sheet_key")
    if json_key_str:
        try:
            json_key_dict = json.loads(json_key_str)  # 문자열을 딕셔너리로 변환
            credential = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
            # credential을 사용하여 Google API에 접근
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Error loading credentials: {e}")
    else:
        print("google_sheet_key environment variable not found.")    
        return None

    gc = gspread.authorize(credential)

    # 개인에 따라 수정 필요 - 스프레드시트 URL 가져오기
    doc = gc.open_by_url(spreadsheet_url)
    sheet = doc.worksheet(notice_type)
    sheet.clear()    

    # 데이터를 리스트의 리스트로 변환하여 한 번에 추가
    data_to_append = [df.columns.tolist()] + df.values.tolist()
    sheet.append_rows(data_to_append)


# 사용 예시
def total_sheet_update(existing_df, notice_list):
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DglQXgnMf4zuBDEG9StgRXgFmaAA7vIhHgAGtWI4TsQ/edit?usp=drive_link"

    # collection = mongo_setting('news_scraping','notice_list')
    # # # 모든 문서 가져오기
    # documents = collection.find()

    # # DataFrame으로 변환
    # new_df = pd.DataFrame(list(documents))
    new_df = pd.DataFrame(notice_list)
    new_df.rename(columns={
        'notice_id': '공고번호',
        'title': '공고명',
        'price': '공고가격(단위: 원)',
        'publishing_agency': '공고 기관',
        'requesting_agency': '수요 기관',
        'start_date': '게시일',
        'end_date': '마감일',
        'link': '링크',
        'type': '비고',
        'notice_class':'공고 유형'
        }, inplace=True)
    # 최신 순으로 정렬
    df = pd.concat([existing_df,new_df],ignore_index=True)
    df.loc[:, '게시일_sort'] = pd.to_datetime(df['게시일'], format='%Y/%m/%d')
    df = df.sort_values(by='게시일_sort', ascending=False).reset_index(drop=True)
    df['공고가격(단위: 원)'] = (
        df['공고가격(단위: 원)']
        .fillna('')  # NaN 값을 빈 문자열로 대체
        .str.replace(',', '', regex=True)  # 쉼표 제거
        .str.replace('원', '', regex=True)  # '원' 제거
        .str.strip()  # 앞뒤 공백 제거
    )

    # 빈 문자열을 NaN으로 변환 후 숫자로 변환
    df['공고가격(단위: 원)'] = pd.to_numeric(df['공고가격(단위: 원)'], errors='coerce')  # 숫자로 변환 불가능한 값은 NaN으로 처리
    df['공고가격(단위: 원)'] = df['공고가격(단위: 원)'].fillna(0).astype(int)
    notice_list = df.loc[:,['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('전체 공고',notice_list,spreadsheet_url)
    notice_list = df.loc[df['공고 유형']=='입찰 공고',['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('입찰 공고',notice_list,spreadsheet_url)
    notice_list = df.loc[df['공고 유형']=='사전 규격',['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('사전 규격',notice_list,spreadsheet_url)

    notice_list = df.loc[df['비고'].str.contains('데이터'),['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('데이터',notice_list,spreadsheet_url)
    notice_list = df.loc[df['비고'].str.contains('인공지능'),['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('인공지능',notice_list,spreadsheet_url)
    notice_list = df.loc[df['비고'].str.contains('ISP/ISMP'),['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('ISP/ISMP',notice_list,spreadsheet_url)
    notice_list = df.loc[df['비고'].str.contains('클라우드'),['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('클라우드',notice_list,spreadsheet_url)


    today = datetime.now()

    # 오늘의 요일 계산 (월=0, 화=1, ..., 일=6)
    today_day_of_week = today.weekday()

    # 금요일 날짜 계산
    def get_friday(date):
        day_of_week = date.weekday()  # 요일 계산
        if day_of_week == 0:  # 월요일인 경우
            return date - timedelta(days=3)  # 전주의 금요일로 이동
        if day_of_week >= 5:  # 토(5), 일(6)
            return date - timedelta(days=(day_of_week - 4))  # 금요일로 이동
        return date  # 금요일이 아닌 경우 그대로 반환

    # 필터링 조건 설정
    if today_day_of_week in [5, 6, 0]:  # 토, 일, 월
        start_date = get_friday(today)  # 금요일부터
    else:  # 화, 수, 목, 금
        start_date = today - timedelta(days=1)  # 전날부터

    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # 조건에 따라 데이터 필터링
    notice_list = df.loc[
        (df['게시일_sort'] >= start_date)&(df['게시일_sort'] <= end_date),
        ['공고 유형', '공고번호', '공고명', '공고가격(단위: 원)', '공고 기관', '수요 기관', '게시일', '마감일', '링크', '비고']
    ]

    print('전체 공고 | 시작 날짜 : {} / 종료 날짜 : {}'.format(start_date,end_date))
    google_sheet_add('새로 올라온 공고',notice_list,spreadsheet_url)
    print("전체 공고 | Data updated and sorted successfully.")


def total_sheet_get():
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DglQXgnMf4zuBDEG9StgRXgFmaAA7vIhHgAGtWI4TsQ/edit?usp=drive_link"

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # 개인에 따라 수정 필요 - 다운로드 받았던 키 값 경로
    json_key_str = os.environ.get("google_sheet_key")
    if json_key_str:
        try:
            json_key_dict = json.loads(json_key_str)  # 문자열을 딕셔너리로 변환
            credential = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
            # credential을 사용하여 Google API에 접근
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Error loading credentials: {e}")
    else:
        print("google_sheet_key environment variable not found.")    
        return None

    gc = gspread.authorize(credential)

    # 개인에 따라 수정 필요 - 스프레드시트 URL 가져오기
    doc = gc.open_by_url(spreadsheet_url)
    sheet = doc.worksheet('전체 공고')
    existing_data = sheet.get_all_values()
    existing_df = pd.DataFrame(existing_data[1:],columns = existing_data[0])
    return existing_df

def category_sheet_update(spreadsheet_url,notice_df,notice_category):

    # collection = mongo_setting('news_scraping','notice_list')
    # # # 모든 문서 가져오기
    # documents = collection.find()

    # # DataFrame으로 변환
    # new_df = pd.DataFrame(list(documents))
    notice_df = notice_df.copy()  # 복사본 생성
    notice_df.loc[:, '게시일_sort'] = pd.to_datetime(notice_df['게시일'], format='%Y/%m/%d')
    # 최신 순으로 정렬
    notice_df = notice_df.sort_values(by='게시일_sort', ascending=False).reset_index(drop=True)
    notice_df['공고가격(단위: 원)'] = (
        notice_df['공고가격(단위: 원)']
        .fillna('')  # NaN 값을 빈 문자열로 대체
        .str.replace(',', '', regex=True)  # 쉼표 제거
        .str.replace('원', '', regex=True)  # '원' 제거
        .str.strip()  # 앞뒤 공백 제거
    )

    # 빈 문자열을 NaN으로 변환 후 숫자로 변환
    notice_df['공고가격(단위: 원)'] = pd.to_numeric(notice_df['공고가격(단위: 원)'], errors='coerce')  # 숫자로 변환 불가능한 값은 NaN으로 처리
    notice_df['공고가격(단위: 원)'] = notice_df['공고가격(단위: 원)'].fillna(0).astype(int)


    notice_list = notice_df.loc[:,['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('전체 공고',notice_list,spreadsheet_url)
    notice_list = notice_df.loc[notice_df['공고 유형']=='입찰 공고',['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('입찰 공고',notice_list,spreadsheet_url)
    notice_list = notice_df.loc[notice_df['공고 유형']=='사전 규격',['공고 유형','공고번호','공고명','공고가격(단위: 원)','공고 기관','수요 기관','게시일','마감일','링크','비고']]
    google_sheet_add('사전 규격',notice_list,spreadsheet_url)


    # 오늘 날짜 계산
    today = datetime.now()

    # 오늘의 요일 계산 (월=0, 화=1, ..., 일=6)
    today_day_of_week = today.weekday()

    # 금요일 날짜 계산
    def get_friday(date):
        day_of_week = date.weekday()  # 요일 계산
        if day_of_week == 0:  # 월요일인 경우
            return date - timedelta(days=3)  # 전주의 금요일로 이동
        if day_of_week >= 5:  # 토(5), 일(6)
            return date - timedelta(days=(day_of_week - 4))  # 금요일로 이동
        return date  # 금요일이 아닌 경우 그대로 반환

    # 필터링 조건 설정
    if today_day_of_week in [5, 6, 0]:  # 토, 일, 월
        start_date = get_friday(today)  # 금요일부터
    else:  # 화, 수, 목, 금
        start_date = today - timedelta(days=1)  # 전날부터

    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today
    end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # 조건에 따라 데이터 필터링
    notice_list = notice_df.loc[
        (notice_df['게시일_sort'] >= start_date)&(notice_df['게시일_sort'] <= end_date),
        ['공고 유형', '공고번호', '공고명', '공고가격(단위: 원)', '공고 기관', '수요 기관', '게시일', '마감일', '링크', '비고']
    ]

    print('{} | 시작 날짜 : {} / 종료 날짜 : {}'.format(notice_category, start_date,end_date))

    google_sheet_add('새로 올라온 공고',notice_list,spreadsheet_url)
    print("{} | Data updated and sorted successfully.".format(notice_category))
    return notice_list

def category_new_data_get(spreadsheet_url,notice_type):

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # 개인에 따라 수정 필요 - 다운로드 받았던 키 값 경로
    json_key_str = os.environ.get("google_sheet_key")
    if json_key_str:
        try:
            json_key_dict = json.loads(json_key_str)  # 문자열을 딕셔너리로 변환
            credential = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
            # credential을 사용하여 Google API에 접근
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Error loading credentials: {e}")
    else:
        print("google_sheet_key environment variable not found.")    
        return None

    gc = gspread.authorize(credential)

    # 개인에 따라 수정 필요 - 스프레드시트 URL 가져오기
    doc = gc.open_by_url(spreadsheet_url)
    sheet = doc.worksheet('새로 올라온 공고')
    new_data = sheet.get_all_values()
    new_df = pd.DataFrame(new_data[1:],columns = new_data[0])
    return new_df