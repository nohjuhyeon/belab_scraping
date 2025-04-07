import os
from g2b_notice_check.google_sheet import category_new_data_get
from g2b_notice_check.email_push import email_sending
import logging
from datetime import datetime

try:
    # 이메일 전송 프로세스 시작 로그
    print("----------------이메일 전송----------------")
    print(datetime.now())

    # 로그 파일 설정
    folder_path = os.environ.get("folder_path")  # 환경 변수에서 폴더 경로 가져오기
    logging.basicConfig(
        filename=folder_path + '/log_list/scheduler.txt', 
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("----------------notice check started----------------")  # 스케줄러 시작 로그 기록

    print("----------------email push started----------------")

    # 1. 인공지능 관련 이메일 전송
    ai_url = "https://docs.google.com/spreadsheets/d/15gZLOTcY-XxlGmkNNMllB4GaJynHiLqtlp6U5PhMMew/edit?usp=drive_link"
    ai_list = category_new_data_get(ai_url)  # 구글 스프레드시트에서 데이터 가져오기
    ai_user = ['jh.noh@belab.co.kr', 'jh.park@belab.co.kr', 'sy.kim@belab.co.kr', 'chyunkim@naver.com']
    # email_sending(ai_list, ai_user, ai_url, '인공지능')  # 이메일 전송

    # 2. 데이터 관련 이메일 전송
    data_url = "https://docs.google.com/spreadsheets/d/10pMJpkFia91wtTROOQt3sje-iT3ztgYjtUjQYGU-xQ8/edit?usp=drive_link"
    data_list = category_new_data_get(data_url)
    data_user = ['jh.noh@belab.co.kr', 'jh.park@belab.co.kr', 'sh.jegal@belab.co.kr', 'chyunkim@naver.com']
    email_sending(data_list, data_user, data_url)

    # 3. 클라우드 관련 이메일 전송
    cloud_url = "https://docs.google.com/spreadsheets/d/14CanIRInmQ2_z2uuNB2gVCjlJsgGRM7c44yOcTSI8eo/edit?usp=drive_link"
    cloud_list = category_new_data_get(cloud_url)
    cloud_user = ['jh.noh@belab.co.kr', 'jh.park@belab.co.kr', 'chyunkim@naver.com']
    email_sending(cloud_list, cloud_user, cloud_url)

    # 4. ISP/ISMP 관련 이메일 전송
    isp_url = "https://docs.google.com/spreadsheets/d/18F6jTsLgsHm1yia9ZOJXD3x_CrYNYnqJY528o09HtrI/edit?usp=drive_link"
    isp_list = category_new_data_get(isp_url)
    isp_user = ['jh.noh@belab.co.kr', 'jh.park@belab.co.kr', 'chyunkim@naver.com']
    email_sending(isp_list, isp_user, isp_url, 'ISP/ISMP')

    # 5. ISP/ISMP 및 클라우드 관련 이메일 전송
    isp_cloud_url = "https://docs.google.com/spreadsheets/d/11lE8ciUVqdN97HJ__ZCRB2RV6IvNwouDv3TkuLFnyUY/edit?usp=drive_link"
    isp_cloud_list = category_new_data_get(isp_cloud_url)
    isp_cloud_user = ['jh.noh@belab.co.kr', 'jh.park@belab.co.kr', 'sy.lee@belab.co.kr']
    email_sending(isp_cloud_list, isp_cloud_user, isp_cloud_url, 'ISP/ISMP, 클라우드')

except (KeyboardInterrupt, SystemExit):
    # 사용자 중단 또는 시스템 종료 시 로그 기록
    print("notice check shut down.")
    logging.info("notice check shut down.")  # 스케줄러 종료 로그 기록

finally:
    # 이메일 전송 완료 메시지 출력
    print("이메일 전송 완료!")
