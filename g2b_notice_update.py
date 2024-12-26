import os 
from g2b_notice_check.google_sheet import total_sheet_update,total_sheet_get
from g2b_notice_check.email_push import email_sending
from dotenv import load_dotenv
import logging
from datetime import datetime
from g2b_notice_check.g2b_notice import notice_collection
from g2b_notice_check.g2b_preparation import preparation_collection

try:
    print("----------------공고 확인 시작----------------")
    print(datetime.now())
    load_dotenv()
    folder_path = os.environ.get("folder_path")
    logging.basicConfig(filename=folder_path+'/log_list/scheduler.txt', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("----------------notice check started----------------") # 스케줄러 시작 로그 기록
    print('나라장터 공고를 찾습니다.')
    existing_df = total_sheet_get()
    notice_list = notice_collection(existing_df)
    preparation_list = preparation_collection(existing_df)
    notice_list.extend(preparation_list)
    # email_sending()
    total_sheet_update(existing_df,notice_list)
    # 스크립트 경로와 인자 설정
except (KeyboardInterrupt, SystemExit):
    print("notice check shut down.")
    logging.info("notice check shut down.") # 스케줄러 종료 로그 기록
finally:
    print("공고 확인 완료!")



