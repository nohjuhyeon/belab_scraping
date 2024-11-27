import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import os 
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from function_list.basic_options import mongo_setting
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def mongodb_add(notice_type, data):
    # MongoDB 연결
    collection = mongo_setting('news_scraping','notice_list')

    # 새로운 데이터를 DataFrame으로 변환
    new_df = pd.DataFrame(data)
    new_df.dropna(subset=['new'], inplace=True)
    new_df.drop(columns=['new'], inplace=True)

    # 기존 데이터의 id 목록 가져오기
    existing_ids = set(doc['notice_id'] for doc in collection.find({}, {'notice_id': 1}))

    # 새로운 데이터에서 기존 id와 중복되지 않는 레코드만 필터링
    new_records = []
    for record in new_df.to_dict('records'):
        if record['id'] not in existing_ids:
            if notice_type == 'notice_list':
                record['notice_class'] = '입찰 공고'
            elif notice_type == 'preparation_list':
                record['notice_class'] = '사전 규격'
            new_records.append(record)

    # 새로운 데이터만 삽입
    if new_records:
        collection.insert_many(new_records)
        print(f"{notice_type}: {len(new_records)} new records added.")
    else:
        print(f"{notice_type}: No new records to add.")

def mongodb_update():
    folder_path = os.environ.get("folder_path")
    
    # 입찰 공고 처리
    json_file_path = f'{folder_path}/g2b_data/notice_list.json'
    data = load_json(json_file_path)
    mongodb_add('notice_list', data)
    
    # 사전 규격 처리
    json_file_path = f'{folder_path}/g2b_data/preparation_list.json'
    data = load_json(json_file_path)
    mongodb_add('preparation_list', data)

if __name__ == "__main__":
    mongodb_update()
