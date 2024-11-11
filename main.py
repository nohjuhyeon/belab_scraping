import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

from news_letter.venture_doctors import venture_doctors
from news_letter.ict_news import ict_news
from news_letter.statistic_bank import statistic_bank
from news_letter.seoul_institute import seoul_institute
from g2b_notice_check.email_push import email_sending
from summary_update import total_update
import os
# 로깅 설정
folder_path = os.getenv("folder_path")
logging.basicConfig(filename=folder_path+'scheduler.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 스케줄러 초기화
scheduler = BackgroundScheduler()

# 매일 함수 실행
scheduler.add_job(email_sending, CronTrigger(hour=9, minute=30))
scheduler.add_job(venture_doctors, CronTrigger(hour=12, minute=0))
scheduler.add_job(statistic_bank, CronTrigger(hour=12, minute=15))
scheduler.add_job(seoul_institute, CronTrigger(hour=12, minute=30))
scheduler.add_job(ict_news, CronTrigger(hour=12, minute=45))
scheduler.add_job(total_update, CronTrigger(hour=13, minute=00))
scheduler.add_job(email_sending, CronTrigger(hour=13, minute=30))


# 스케줄러 시작
scheduler.start()

print("Scheduler started...")
logging.info("Scheduler started...") # 스케줄러 시작 로그 기록

# 메인 프로그램이 종료되지 않도록 유지
try:
    while True:
        time.sleep(1)  # Keep the main thread alive
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("Scheduler shut down.")
    logging.info("Scheduler shut down.") # 스케줄러 종료 로그 기록
