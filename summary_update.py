from news_letter.naver_new import naver_news
import os
import logging
from datetime import datetime
from git_hub_commit import git_commit
from dotenv import load_dotenv

def total_update():
    # 환경 변수 로드
    loaded = load_dotenv(dotenv_path='/app/belab_scraping/.env')
    # 네이버 뉴스 데이터 수집 및 업데이트
    naver_news()

try:
    # GitHub 커밋 실행
    git_commit()

    # 뉴스 요약 업데이트 시작 로그
    print("----------------뉴스 요약 업데이트 시작----------------")
    print(datetime.now())

    # 환경 변수 로드
    load_dotenv()

    # 로그 파일 설정
    folder_path = os.environ.get("folder_path")  # 환경 변수에서 폴더 경로 가져오기
    logging.basicConfig(
        filename=folder_path + '/log_list/scheduler.txt', 
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # 스케줄러 시작 로그 기록
    logging.info("----------------news summarization started----------------")

    # 전체 업데이트 실행
    total_update()

except (KeyboardInterrupt, SystemExit):
    # 사용자 중단 또는 시스템 종료 시 로그 기록
    print("summarization shut down.")
    logging.info("summarization shut down.")  # 스케줄러 종료 로그 기록

finally:
    # GitHub 커밋 실행 및 뉴스 요약 완료 메시지 출력
    git_commit()
    print("뉴스 요약 업데이트 완료!")
