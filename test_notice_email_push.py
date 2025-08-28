import os
from g2b_notice_check.google_sheet import category_new_data_get
from g2b_notice_check.email_push import email_sending
from function_list.basic_options import mongo_setting
import logging
from datetime import datetime
import subprocess
from dotenv import load_dotenv
loaded = load_dotenv(dotenv_path='/app/belab_scraping/.env')
try:
    mongo_client,collection = mongo_setting("news_scraping", "notice_list")  # MongoDB 설정
    # 이메일 전송 프로세스 시작 로그
    print("----------------이메일 전송----------------")
    print(datetime.now())
    # 로그 파일 설정
    folder_path = os.environ.get("folder_path")  # 환경 변수에서 폴더 경로 가져오기

    if folder_path is None:
        print('folder_path is None')

    # 1. 인공지능 관련 이메일 전송
    ai_url = "https://docs.google.com/spreadsheets/d/1Rd6o2rBays25jvcz6SGf03Pvr3ci5epfzlI2TmvWTQI/edit?usp=sharing"
    ai_keyword = '인공지능'
    ai_list = category_new_data_get(ai_keyword,collection)  # 구글 스프레드시트에서 데이터 가져오기
    ai_user = ['njh2720@gmail.com']
    email_sending(ai_list, ai_user, ai_url, ai_keyword)  # 이메일 전송

    # 2. 데이터 관련 이메일 전송
    data_url = "https://docs.google.com/spreadsheets/d/1tTaqo_BPZvHEKx_OcFOj3RoFr-e_9i5-ftPW4hS4Qq0/edit?usp=sharing"
    data_keyword = '데이터'
    data_list = category_new_data_get(data_keyword,collection)
    data_user = ['njh2720@gmail.com']
    email_sending(data_list, data_user, data_url,data_keyword)

    # 3. 클라우드 관련 이메일 전송
    cloud_url = "https://docs.google.com/spreadsheets/d/1YJI1NrcLaHiTtyjhK071MiIYQ36G0LWJ4QSfgE67paU/edit?usp=sharing"
    cloud_keyword = '클라우드'
    cloud_list = category_new_data_get(cloud_keyword,collection)
    cloud_user = ['njh2720@gmail.com']
    email_sending(cloud_list, cloud_user, cloud_url,cloud_keyword)

    # 4. 네트워크/보안 관련 이메일 전송
    network_security_url = "https://docs.google.com/spreadsheets/d/12aoE7vXB7JNICh93q0NaabCdF8wsLiBEX8WN8fiZDxI/edit?usp=sharing"
    network_security_keyword = '네트워크 및 보안'
    network_security_list = category_new_data_get(network_security_keyword,collection)
    network_security_user = ['njh2720@gmail.com']
    email_sending(network_security_list, network_security_user, network_security_url,network_security_keyword)

    # 5. AR/VR 및 메타버스 관련 이메일 전송
    metaverse_url = "https://docs.google.com/spreadsheets/d/1X5i6DflM_ZBE_SK4uEe2hhw-f6F1ZGr_4akRDcrGW4Q/edit?usp=sharing"
    metaverse_keyword = 'AR/VR 및 메타버스'
    metaverse_list = category_new_data_get(metaverse_keyword,collection)
    metaverse_user = ['njh2720@gmail.com']
    email_sending(metaverse_list, metaverse_user, metaverse_url,metaverse_keyword)

    # 6. 소프트웨어 개발 및 관리 관련 이메일 전송
    software_url = "https://docs.google.com/spreadsheets/d/1jL5PAmWhI5Uv3Va5oW6zhbumfemHQzCqoOGUZnfujf8/edit?usp=sharing"
    software_keyword = "소프트웨어 개발 및 관리"
    software_list = category_new_data_get(software_keyword,collection)
    software_user = ['njh2720@gmail.com']
    email_sending(software_list, software_user, software_url,software_keyword)

    # 7. 블록체인 관련 이메일 전송
    blockchain_url = "https://docs.google.com/spreadsheets/d/1V4LvEm_nI8iOy0784WMDERB-ENLbMJeQ1U3uTvgmEcU/edit?usp=sharing"
    blockchain_keyword = '블록체인'
    blockchain_list = category_new_data_get(blockchain_keyword,collection)
    blockchain_user = ['njh2720@gmail.com']
    email_sending(blockchain_list, blockchain_user, blockchain_url,blockchain_keyword)

    # 8. IoT 관련 이메일 전송
    IoT_url = "https://docs.google.com/spreadsheets/d/19aYGVI6FIbyfQf9zyEqqpi8EeITo2WCVWNRT-o1V3o4/edit?usp=sharing"
    IoT_keyword = 'IoT'
    IoT_list = category_new_data_get(IoT_keyword,collection)
    IoT_user = ['njh2720@gmail.com']
    email_sending(IoT_list, IoT_user, IoT_url,IoT_keyword)


    # 9. ISP/ISMP 관련 이메일 전송
    isp_url = "https://docs.google.com/spreadsheets/d/18F6jTsLgsHm1yia9ZOJXD3x_CrYNYnqJY528o09HtrI/edit?usp=drive_link"
    isp_keyword = 'ISP/ISMP'
    isp_list = category_new_data_get(isp_keyword,collection)
    isp_user = ['njh2720@gmail.com']
    email_sending(isp_list, isp_user, isp_url, isp_keyword)


except (KeyboardInterrupt, SystemExit):
    # 사용자 중단 또는 시스템 종료 시 로그 기록
    print("notice check shut down.")

finally:
    mongo_client.close()
    # 이메일 전송 완료 메시지 출력
    print("이메일 전송 완료!")
