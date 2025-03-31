import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
from datetime import datetime, timedelta
import os 
import pandas as pd

def notice_date_modify(date_time):
    """
    날짜 문자열을 datetime 객체로 변환.
    :param date_time: 날짜 문자열
    :return: 변환된 datetime 객체
    """
    try:
        new_date = pd.to_datetime(date_time, format='%Y-%m-%d %H:%M:%S')
    except:
        new_date = pd.to_datetime(date_time, format='%Y-%m-%d')
    return new_date


def google_sheet_add(notice_type, df, spreadsheet_url):
    """
    Google Sheet에 데이터를 추가.
    :param notice_type: 시트 이름
    :param df: 추가할 데이터 (DataFrame)
    :param spreadsheet_url: Google Sheet URL
    """
    # Google API 인증 설정
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    json_key_str = os.environ.get("google_sheet_key")
    if json_key_str:
        try:
            json_key_dict = json.loads(json_key_str)
            credential = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류: {e}")
            return
        except Exception as e:
            print(f"인증 정보 로드 오류: {e}")
            return
    else:
        print("환경 변수 google_sheet_key를 찾을 수 없음.")
        return

    # Google Sheet 접근 및 데이터 추가
    gc = gspread.authorize(credential)
    doc = gc.open_by_url(spreadsheet_url)
    sheet = doc.worksheet(notice_type)
    sheet.clear()
    data_to_append = [df.columns.tolist()] + df.values.tolist()
    sheet.append_rows(data_to_append)

# 사용 예시
def total_sheet_update(existing_df, notice_list):
    """
    전체 공고 데이터를 업데이트하고 Google Sheet에 반영.

    Args:
        - existing_df(DataFrame): 기존 데이터
        - notice_list(List[dict]): 새로 수집된 공고 데이터 
    """
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DglQXgnMf4zuBDEG9StgRXgFmaAA7vIhHgAGtWI4TsQ/edit?usp=drive_link"

    # 새 데이터 병합 및 정렬
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
        'notice_class': '공고 유형'
    }, inplace=True)
    df = pd.concat([existing_df, new_df], ignore_index=True)
    df['게시일_sort'] = df['게시일'].apply(notice_date_modify)
    df = df.sort_values(by='게시일_sort', ascending=False).reset_index(drop=True)

    # 공고 가격 처리
    df['공고가격(단위: 원)'] = (
        df['공고가격(단위: 원)']
        .fillna('')
        .str.replace(',', '', regex=True)
        .str.replace('원', '', regex=True)
        .str.strip()
    )
    df['공고가격(단위: 원)'] = pd.to_numeric(df['공고가격(단위: 원)'], errors='coerce').fillna(0).astype(int)

    # Google Sheet에 데이터 추가
    notice_list = df.loc[:, ['공고 유형', '공고번호', '공고명', '공고가격(단위: 원)', '공고 기관', '수요 기관', '게시일', '마감일', '링크', '비고']]
    google_sheet_add('전체 공고', notice_list, spreadsheet_url)

    # 공고 유형별로 데이터 추가
    for notice_type in ['입찰 공고', '사전 규격']:
        filtered_list = df.loc[df['공고 유형'] == notice_type, ['공고 유형', '공고번호', '공고명', '공고가격(단위: 원)', '공고 기관', '수요 기관', '게시일', '마감일', '링크', '비고']]
        google_sheet_add(notice_type, filtered_list, spreadsheet_url)

    # 특정 키워드 포함 공고 추가
    keywords = ['데이터', '인공지능', 'ISP/ISMP', '클라우드']
    for keyword in keywords:
        filtered_list = df.loc[df['비고'].str.contains(keyword), ['공고 유형', '공고번호', '공고명', '공고가격(단위: 원)', '공고 기관', '수요 기관', '게시일', '마감일', '링크', '비고']]
        google_sheet_add(keyword, filtered_list, spreadsheet_url)

    # 새로 올라온 공고 필터링 및 추가
    today = datetime.now()
    # 오늘의 요일 계산 (월=0, 화=1, ..., 일=6)
    today_day_of_week = today.weekday()

    day_of_week = today.weekday()  # 요일 계산
    if today_day_of_week in [5, 6, 0]:  # 토, 일, 월
        if day_of_week == 0:  # 월요일인 경우
            start_date =  today - timedelta(days=3)  # 전주의 금요일로 이동
        if day_of_week >= 5:  # 토(5), 일(6)
            start_date =  today - timedelta(days=(day_of_week - 4))  # 금요일로 이동
        else:
            start_date = today
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
    """
    Google Sheet에서 전체 공고 데이터를 가져옴.
    
    Returns:
        - existing_df(DataFrame): 기존 공고 데이터
    """
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1DglQXgnMf4zuBDEG9StgRXgFmaAA7vIhHgAGtWI4TsQ/edit?usp=drive_link"

    # Google API 인증 설정
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    json_key_str = os.environ.get("google_sheet_key")
    if json_key_str:
        try:
            json_key_dict = json.loads(json_key_str)
            credential = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류: {e}")
            return None
        except Exception as e:
            print(f"인증 정보 로드 오류: {e}")
            return None
    else:
        print("환경 변수 google_sheet_key를 찾을 수 없음.")
        return None

    # Google Sheet에서 데이터 가져오기
    gc = gspread.authorize(credential)
    doc = gc.open_by_url(spreadsheet_url)
    sheet = doc.worksheet('전체 공고')
    existing_data = sheet.get_all_values()
    existing_df = pd.DataFrame(existing_data[1:], columns=existing_data[0])
    return existing_df



def category_sheet_update(spreadsheet_url, notice_df, notice_category):
    """
    특정 카테고리 공고 데이터를 업데이트하고 Google Sheet에 반영.

    Args:
        - spreadsheet_url(str): Google Sheet URL
        - notice_df(DataFrame): 공고 데이터 
        - notice_category(str): 카테고리 이름
    """
    notice_df = notice_df.copy()
    notice_df['게시일_sort'] = notice_df['게시일'].apply(notice_date_modify)
    notice_df = notice_df.sort_values(by='게시일_sort', ascending=False).reset_index(drop=True)

    # 공고 가격 처리
    notice_df['공고가격(단위: 원)'] = (
        notice_df['공고가격(단위: 원)']
        .fillna('')
        .str.replace(',', '', regex=True)
        .str.replace('원', '', regex=True)
        .str.strip()
    )
    notice_df['공고가격(단위: 원)'] = pd.to_numeric(notice_df['공고가격(단위: 원)'], errors='coerce').fillna(0).astype(int)

    # Google Sheet에 데이터 추가
    notice_list = notice_df.loc[:, ['공고 유형', '공고번호', '공고명', '공고가격(단위: 원)', '공고 기관', '수요 기관', '게시일', '마감일', '링크', '비고']]
    google_sheet_add('전체 공고', notice_list, spreadsheet_url)

    # 특정 날짜 범위 공고 필터링 및 추가
    today = datetime.now()
    start_date = today - timedelta(days=1)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    filtered_list = notice_df.loc[
        (notice_df['게시일_sort'] >= start_date) & (notice_df['게시일_sort'] <= end_date),
        ['공고 유형', '공고번호', '공고명', '공고가격(단위: 원)', '공고 기관', '수요 기관', '게시일', '마감일', '링크', '비고']
    ]
    google_sheet_add('새로 올라온 공고', filtered_list, spreadsheet_url)
    print(f"{notice_category} | 데이터 업데이트 및 정렬 완료.")


def category_new_data_get(spreadsheet_url):
    """
    Google Sheet에서 새로 올라온 공고 데이터를 가져옴.

    Args:
        spreadsheet_url(str): Google Sheet URL

    Returns:
        - new_df(DataFrame): 새 공고 데이터 
    """

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    json_key_str = os.environ.get("google_sheet_key")
    if json_key_str:
        try:
            json_key_dict = json.loads(json_key_str)
            credential = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류: {e}")
            return None
        except Exception as e:
            print(f"인증 정보 로드 오류: {e}")
            return None
    else:
        print("환경 변수 google_sheet_key를 찾을 수 없음.")
        return None
    # Google Sheet에서 데이터 가져오기
    gc = gspread.authorize(credential)
    doc = gc.open_by_url(spreadsheet_url)
    sheet = doc.worksheet('새로 올라온 공고')
    new_data = sheet.get_all_values()
    new_df = pd.DataFrame(new_data[1:], columns=new_data[0])
    return new_df
