import os 
from g2b_notice_check.google_sheet_send import google_sheet_update
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
    # notice_collection()
    # preparation_collection()
    # email_sending()

    google_sheet_update()
    # 스크립트 경로와 인자 설정
except (KeyboardInterrupt, SystemExit):
    print("notice check shut down.")
    logging.info("notice check shut down.") # 스케줄러 종료 로그 기록
finally:
    print("공고 확인 완료!")



