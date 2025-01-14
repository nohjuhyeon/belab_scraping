import os 
from g2b_notice_check.google_sheet import total_sheet_update,total_sheet_get, category_sheet_update
from dotenv import load_dotenv
import logging
from datetime import datetime
from g2b_notice_check.g2b_notice import notice_collection
from g2b_notice_check.g2b_preparation import preparation_collection
from function_list.basic_options import mongo_setting
import pandas as pd
try:
    print("----------------공고 확인 시작----------------")
    print(datetime.now())
    load_dotenv()
    folder_path = os.environ.get("folder_path")
    logging.basicConfig(filename=folder_path+'/log_list/scheduler.txt', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("----------------notice check started----------------") # 스케줄러 시작 로그 기록
    # 나라장터 데이터 수집
    print('나라장터 공고를 찾습니다.')
    # existing_df = total_sheet_get()
    collection = mongo_setting('news_scraping','notice_list')
    results = collection.find({},{'_id':0})
    existing_df = [i for i in results]
    existing_df = pd.DataFrame(existing_df)
    existing_df.rename(columns={
        'notice_id': '공고번호',
        'title': '공고명',
        'price': '공고가격(단위: 원)',
        'publishing_agency': '공고 기관',
        'requesting_agency': '수요 기관',
        'start_date': '게시일',
        'end_date': '마감일',
        'link': '링크',
        'type': '비고',
        'notice_class':'공고 유형'
        }, inplace=True)
    # notice_list = []
    notice_list = notice_collection(existing_df)
    # preparation_list = preparation_collection(existing_df)
    # notice_list.extend(preparation_list)
    # 전체 공고 업데이트
    total_sheet_update(existing_df, notice_list)

    # 카테고리별 공고 업데이트
    notice_df = total_sheet_get()

    ## 인공지능 공고 업데이트
    ai_url = "https://docs.google.com/spreadsheets/d/15gZLOTcY-XxlGmkNNMllB4GaJynHiLqtlp6U5PhMMew/edit?usp=drive_link"
    ai_df = notice_df.loc[notice_df['비고'].str.contains('인공지능')]
    ai_list = category_sheet_update(ai_url,ai_df,'인공지능')

    ## 데이터 공고 업데이트
    data_url = "https://docs.google.com/spreadsheets/d/10pMJpkFia91wtTROOQt3sje-iT3ztgYjtUjQYGU-xQ8/edit?usp=drive_link"
    data_df = notice_df.loc[notice_df['비고'].str.contains('데이터')]
    category_sheet_update(data_url,data_df,'데이터')

    ## 클라우드 공고 업데이트
    cloud_url = "https://docs.google.com/spreadsheets/d/14CanIRInmQ2_z2uuNB2gVCjlJsgGRM7c44yOcTSI8eo/edit?usp=drive_link"
    cloud_df = notice_df.loc[notice_df['비고'].str.contains('클라우드')]
    category_sheet_update(cloud_url,cloud_df,'클라우드')

    ## isp/ismp 공고 업데이트
    isp_url = "https://docs.google.com/spreadsheets/d/18F6jTsLgsHm1yia9ZOJXD3x_CrYNYnqJY528o09HtrI/edit?usp=drive_link"
    isp_df = notice_df.loc[notice_df['비고'].str.contains('ISP/ISMP')]
    category_sheet_update(isp_url,isp_df,'ISP/ISMP')

    ## isp/ismp, cloud 공고 업데이트
    isp_cloud_url = "https://docs.google.com/spreadsheets/d/11lE8ciUVqdN97HJ__ZCRB2RV6IvNwouDv3TkuLFnyUY/edit?usp=drive_link"
    isp_cloud_df = notice_df.loc[(notice_df['비고'].str.contains('ISP/ISMP'))|(notice_df['비고'].str.contains('클라우드'))]
    category_sheet_update(isp_cloud_url,isp_cloud_df,'ISP/ISMP, 클라우드')

except (KeyboardInterrupt, SystemExit):
    print("notice check shut down.")
    logging.info("notice check shut down.") # 스케줄러 종료 로그 기록
finally:
    print("공고 확인 완료!")



