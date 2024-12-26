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

    print("Data updated and sorted successfully.")

# 사용 예시
def total_sheet_update(existing_df,notice_list):
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DglQXgnMf4zuBDEG9StgRXgFmaAA7vIhHgAGtWI4TsQ/edit?usp=drive_link"

    # # collection = mongo_setting('news_scraping','new_notice_list')
    # # # 모든 문서 가져오기
    # # documents = collection.find()

    # # DataFrame으로 변환
    # df = pd.DataFrame(list(documents))
    new_df = pd.DataFrame(notice_list)
    new_df.rename(columns={
        'notice_id': '공고번호',
        'title': '공고명',
        'price': '공고 가격',
        'publishing_agency': '공고 기관',
        'requesting_agency': '수요 기관',
        'start_date': '개시일',
        'end_date': '마감일',
        'link': '링크',
        'type': '비고',
        'notice_class':'공고 유형'
        }, inplace=True)
    new_df['개시일_sort'] = pd.to_datetime(new_df['개시일'], format='%Y/%m/%d')
    # 최신 순으로 정렬
    df = pd.concat([existing_df,new_df],ignore_index=True)
    df = df.sort_values(by='개시일_sort', ascending=False).reset_index(drop=True)


    notice_list = df.loc[:,['공고 유형','공고번호','공고명','공고 가격','공고 기관','수요 기관','개시일','마감일','링크','비고']]
    google_sheet_add('전체 공고',notice_list,spreadsheet_url)
    notice_list = df.loc[df['공고 유형']=='입찰 공고',['공고 유형','공고번호','공고명','공고 가격','공고 기관','수요 기관','개시일','마감일','링크','비고']]
    google_sheet_add('입찰 공고',notice_list,spreadsheet_url)
    notice_list = df.loc[df['공고 유형']=='사전 규격',['공고 유형','공고번호','공고명','공고 가격','공고 기관','수요 기관','개시일','마감일','링크','비고']]
    google_sheet_add('사전 규격',notice_list,spreadsheet_url)

    notice_list = df.loc[df['비고'].str.contains('데이터'),['공고 유형','공고번호','공고명','공고 가격','공고 기관','수요 기관','개시일','마감일','링크','비고']]
    google_sheet_add('데이터',notice_list,spreadsheet_url)
    notice_list = df.loc[df['비고'].str.contains('인공 지능'),['공고 유형','공고번호','공고명','공고 가격','공고 기관','수요 기관','개시일','마감일','링크','비고']]
    google_sheet_add('인공 지능',notice_list,spreadsheet_url)
    notice_list = df.loc[df['비고'].str.contains('ISP/ISMP'),['공고 유형','공고번호','공고명','공고 가격','공고 기관','수요 기관','개시일','마감일','링크','비고']]
    google_sheet_add('ISP/ISMP',notice_list,spreadsheet_url)
    notice_list = df.loc[df['비고'].str.contains('클라우드'),['공고 유형','공고번호','공고명','공고 가격','공고 기관','수요 기관','개시일','마감일','링크','비고']]
    google_sheet_add('클라우드',notice_list,spreadsheet_url)


    yesterday = datetime.now() - timedelta(days=1)
    today = datetime.now()
    yesterday = yesterday.strftime('%Y/%m/%d')
    today = today.strftime('%Y/%m/%d')
    notice_list=df.loc[(df['개시일']==today)|(df['개시일']==yesterday),['공고 유형','공고번호','공고명','공고 가격','공고 기관','수요 기관','개시일','마감일','링크','비고']]
    google_sheet_add('새로 올라온 공고',notice_list,spreadsheet_url)


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

# google_sheet_update()
