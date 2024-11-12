import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import numpy as np
from datetime import datetime, timedelta
import os 
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def google_sheet_add(notice_type,data):
        # OAuth2 인증을 위한 서비스 계정 키 파일 경로
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # 개인에 따라 수정 필요 - 다운로드 받았던 키 값 경로
    # json_key_path = "C:/develops/belab_scraping/google_sheet_key.json"
    json_key_str = os.environ.get("google_sheet_key")
    if json_key_str:
        try:
            json_key_dict = json.loads(json_key_str)  # 문자열을 딕셔너리로 변환
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            credential = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
            # credential을 사용하여 Google API에 접근
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Error loading credentials: {e}")
    else:
        print("google_sheet_key environment variable not found.")    
    credential = ServiceAccountCredentials.from_json_keyfile_dict(json_key_dict, scope)
    gc = gspread.authorize(credential)

    # 개인에 따라 수정 필요 - 스프레드시트 URL 가져오기
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1v61bDfjX0TKnZDKhttzyV9N_LJekA5TxGWCwXW0AXKk/edit?pli=1&gid=0#gid=0"

    doc = gc.open_by_url(spreadsheet_url)
    sheet = doc.worksheet(notice_type)

    df,today_df = notice_add(data,notice_type,sheet)
    sheet.clear()    
    # 개인에 따라 수정 필요 - 시트 선택하기 (시트명을 그대로 입력해주면 된다.)
    # 정렬된 데이터를 스프레드시트에 다시 씀
    sheet.append_row(df.columns.tolist())  # 헤더 추가
    for index, row in df.iterrows():
        sheet.append_row(row.tolist())

    print("Data updated and sorted successfully.")
    return today_df

def notice_add(data,notice_type,sheet):
    update_date = datetime.now() - timedelta(days=1)

    # 어제 날짜를 원하는 형식으로 포맷팅
    update_date = update_date.strftime('%Y/%m/%d')
    if notice_type == '새로 올라온 공고':
        data.drop_duplicates(subset='공고번호', keep='first', inplace=True)
        data.sort_values(by='공고 유형',ascending=False, inplace=True)
        return data,data
    else:
        if notice_type == '입찰 공고':
            # 기존 데이터를 읽어옴
            existing_data = sheet.get_all_records()
            existing_df = pd.DataFrame(existing_data)

            # JSON 데이터를 데이터프레임으로 변환
            new_df = pd.DataFrame(data)
            new_df.dropna(subset=['new_notice', 'notice_type'], inplace=True)
            new_df.drop(columns=['new_notice'], inplace=True)

            # 컬럼 이름 변경
            new_df.rename(columns={
                'notice_id': '공고번호',
                'notice_title': '공고명',
                'notice_price': '공고 가격',
                'publishing_agency': '공고 기관',
                'requesting_agency': '수요 기관',
                'notice_start_date': '개시일',
                'notice_end_date': '마감일',
                'notice_link': '링크',
                'notice_type': '비고'
            }, inplace=True)
        elif notice_type == '사전 규격':
            existing_data = sheet.get_all_records()
            existing_df = pd.DataFrame(existing_data)

            # JSON 데이터를 데이터프레임으로 변환
            new_df = pd.DataFrame(data)
            new_df.dropna(subset=['new_preparation', 'preparation_type'], inplace=True)
            new_df.drop(columns=['new_preparation'], inplace=True)
            # 컬럼 이름 변경
            new_df.rename(columns={
                'preparation_id': '공고번호',
                'preparation_title': '공고명',
                'preparation_price': '공고 가격',
                'publishing_agency': '공고 기관',
                'requesting_agency': '수요 기관',
                'preparation_start_date': '개시일',
                'preparation_end_date': '마감일',
                'preparation_link': '링크',
                'preparation_type': '비고'
            }, inplace=True)
            # 개시일과 마감일을 datetime으로 변환

        # 기존 데이터와 새 데이터를 합침
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        # NaN 값을 빈 문자열로 대체
        combined_df.replace({np.nan: ''}, inplace=True)
        combined_df.drop_duplicates(subset='공고번호', keep='first', inplace=True)

        # 개시일 기준으로 데이터프레임 정렬
        combined_df.sort_values(by='개시일',ascending=False, inplace=True)
        # '비고' 열에서 'ai_preparation' 값을 '인공지능 관련 공고'로 변경
        combined_df.loc[combined_df['비고'] == 'ai_preparation', '비고'] = '인공 지능'
        combined_df.loc[combined_df['비고'] == 'ai_notice', '비고'] = '인공 지능'

        # '비고' 열에서 'check' 값을 '검토가 필요한 공고'로 변경
        combined_df.loc[combined_df['비고'] == 'check', '비고'] = '검토 필요'
        today_df=combined_df.loc[combined_df['개시일']==update_date]
        today_df['공고 유형']=notice_type
        columns = ['공고 유형'] + [col for col in today_df.columns if col != '공고 유형']
        today_df = today_df[columns]
        # 기존 시트 데이터를 모두 삭제
        return combined_df,today_df

# 사용 예시
def google_sheet_update():
    folder_path = os.environ.get("folder_path")
    json_file_path = folder_path+'notice_list.json'

    # JSON 파일에서 데이터 로드
    data = load_json(json_file_path)
    # 스프레드시트에 데이터 업데이트
    notice_type = '입찰 공고'
    new_notice_df = google_sheet_add(notice_type,data)
    
    folder_path = os.environ.get("folder_path")
    json_file_path = folder_path+'preparation_list.json'
    # JSON 파일에서 데이터 로드
    data = load_json(json_file_path)
    notice_type = '사전 규격'
    # 스프레드시트에 데이터 업데이트
    new_preparation_df = google_sheet_add(notice_type,data)

    new_df = pd.concat([new_notice_df, new_preparation_df], ignore_index=True)
    notice_type = '새로 올라온 공고'
    google_sheet_add(notice_type,new_df)

