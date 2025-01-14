import os 
from g2b_notice_check.google_sheet import category_new_data_get
from g2b_notice_check.email_push import email_sending
from dotenv import load_dotenv
import logging
from datetime import datetime

try:
    print("----------------이메일 전송----------------")
    print(datetime.now())
    load_dotenv()
    folder_path = os.environ.get("folder_path")
    logging.basicConfig(filename=folder_path+'/log_list/scheduler.txt', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("----------------notice check started----------------") # 스케줄러 시작 로그 기록
    print("----------------email push started----------------")
    ## 인공지능 이메일 전송
    ai_url = "https://docs.google.com/spreadsheets/d/15gZLOTcY-XxlGmkNNMllB4GaJynHiLqtlp6U5PhMMew/edit?usp=drive_link"
    ai_list = category_new_data_get(ai_url, '인공지능')
    # ai_user = ['jh.noh@belab.co.kr','jh.park@belab.co.kr','sy.kim@belab.co.kr','ma.han@belab.co.kr','chyunkim@naver.com']
    ai_user = ['njh0205@naver.com','njh2720@gmail.com','jh.noh@belab.co.kr']
    email_sending(ai_list, ai_user,ai_url, '인공지능')

    ## 데이터 이메일 전송
    data_url = "https://docs.google.com/spreadsheets/d/10pMJpkFia91wtTROOQt3sje-iT3ztgYjtUjQYGU-xQ8/edit?usp=drive_link"
    data_list = category_new_data_get(data_url, '데이터')
    # data_user = ['jh.noh@belab.co.kr','jh.park@belab.co.kr','sh.jegal@belab.co.kr','chyunkim@naver.com']
    data_user = ['njh0205@naver.com','njh2720@gmail.com','jh.noh@belab.co.kr']
    email_sending(data_list, data_user,data_url, '데이터')

    ## 클라우드 이메일 전송
    cloud_url = "https://docs.google.com/spreadsheets/d/14CanIRInmQ2_z2uuNB2gVCjlJsgGRM7c44yOcTSI8eo/edit?usp=drive_link"
    cloud_list = category_new_data_get(cloud_url, '클라우드')
    # cloud_user = ['jh.noh@belab.co.kr','jh.park@belab.co.kr','chyunkim@naver.com']
    cloud_user = ['njh0205@naver.com','njh2720@gmail.com','jh.noh@belab.co.kr']
    email_sending(cloud_list, cloud_user,cloud_url, '클라우드')

    ## isp/ismp 이메일 전송
    isp_url = "https://docs.google.com/spreadsheets/d/18F6jTsLgsHm1yia9ZOJXD3x_CrYNYnqJY528o09HtrI/edit?usp=drive_link"
    isp_list = category_new_data_get(isp_url, 'ISP/ISMP')
    # isp_user = ['jh.noh@belab.co.kr','jh.park@belab.co.kr','chyunkim@naver.com']
    isp_user = ['njh0205@naver.com','njh2720@gmail.com','jh.noh@belab.co.kr']
    email_sending(isp_list, isp_user,isp_url, 'ISP/ISMP')

    ## isp/ismp, 클라우드 이메일 전송
    isp_cloud_url = "https://docs.google.com/spreadsheets/d/11lE8ciUVqdN97HJ__ZCRB2RV6IvNwouDv3TkuLFnyUY/edit?usp=drive_link"
    isp_cloud_list = category_new_data_get(isp_cloud_url, 'ISP/ISMP, 클라우드')
    # isp_cloud_user = ['jh.noh@belab.co.kr','jh.park@belab.co.kr','sy.lee@belab.co.kr']
    isp_cloud_user = ['njh0205@naver.com','njh2720@gmail.com','jh.noh@belab.co.kr']
    email_sending(isp_cloud_list, isp_cloud_user,isp_cloud_url, 'ISP/ISMP, 클라우드')


except (KeyboardInterrupt, SystemExit):
    print("notice check shut down.")
    logging.info("notice check shut down.") # 스케줄러 종료 로그 기록
finally:
    print("이메일 전송 완료!")



