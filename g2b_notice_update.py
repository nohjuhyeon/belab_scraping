import os
from g2b_notice_check.google_sheet import (
    total_sheet_update,
    total_sheet_get,
    category_sheet_update,
)
import logging
from datetime import datetime
from g2b_notice_check.g2b_notice import notice_collection
from git_hub_commit import git_commit
from g2b_notice_check.g2b_preparation import preparation_collection
from function_list.basic_options import mongo_setting
import pandas as pd

try:
    # GitHub 커밋 실행
    git_commit()

    # 공고 확인 프로세스 시작 로그
    print("----------------공고 확인 시작----------------")
    print(datetime.now())

    # 로그 파일 설정
    folder_path = os.environ.get("folder_path")  # 환경 변수에서 폴더 경로 가져오기

    # 나라장터 데이터 수집 시작
    print("나라장터 공고를 찾습니다.")
    collection = mongo_setting("news_scraping", "notice_list")  # MongoDB 설정
    results = collection.find({}, {"_id": 0})  # MongoDB에서 기존 공고 데이터 가져오기
    existing_df = [i for i in results]  # 결과를 리스트로 변환
    existing_df = pd.DataFrame(existing_df)  # DataFrame으로 변환

    # 컬럼 이름 변경 (가독성을 위해 한글로 변경)
    existing_df.rename(
        columns={
            "notice_id": "공고번호",
            "title": "공고명",
            "price": "공고가격(단위: 원)",
            "publishing_agency": "공고 기관",
            "requesting_agency": "수요 기관",
            "start_date": "게시일",
            "end_date": "마감일",
            "link": "링크",
            "type": "비고",
            "notice_class": "공고 유형",
        },
        inplace=True,
    )

    # 공고 데이터 필터링 및 수집
    notice_list = notice_collection(existing_df)

    # 전체 공고 업데이트
    total_sheet_update(existing_df, notice_list)

    # 카테고리별 공고 업데이트를 위한 전체 공고 데이터 가져오기
    notice_df = total_sheet_get()

    # 1. 인공지능 카테고리 공고 업데이트
    ai_url = "https://docs.google.com/spreadsheets/d/15gZLOTcY-XxlGmkNNMllB4GaJynHiLqtlp6U5PhMMew/edit?usp=drive_link"
    ai_df = notice_df.loc[
        notice_df["비고"].str.contains("인공지능")
    ]  # '비고' 컬럼에서 '인공지능' 포함 데이터 필터링
    category_sheet_update(ai_url, ai_df, "인공지능")

    # 2. 데이터 카테고리 공고 업데이트
    data_url = "https://docs.google.com/spreadsheets/d/10pMJpkFia91wtTROOQt3sje-iT3ztgYjtUjQYGU-xQ8/edit?usp=drive_link"
    data_df = notice_df.loc[
        notice_df["비고"].str.contains("데이터")
    ]  # '비고' 컬럼에서 '데이터' 포함 데이터 필터링
    category_sheet_update(data_url, data_df, "데이터")

    # 3. 클라우드 카테고리 공고 업데이트
    cloud_url = "https://docs.google.com/spreadsheets/d/14CanIRInmQ2_z2uuNB2gVCjlJsgGRM7c44yOcTSI8eo/edit?usp=drive_link"
    cloud_df = notice_df.loc[
        notice_df["비고"].str.contains("클라우드")
    ]  # '비고' 컬럼에서 '클라우드' 포함 데이터 필터링
    category_sheet_update(cloud_url, cloud_df, "클라우드")

    # 4. ISP/ISMP 카테고리 공고 업데이트
    isp_url = "https://docs.google.com/spreadsheets/d/18F6jTsLgsHm1yia9ZOJXD3x_CrYNYnqJY528o09HtrI/edit?usp=drive_link"
    isp_df = notice_df.loc[
        notice_df["비고"].str.contains("ISP/ISMP")
    ]  # '비고' 컬럼에서 'ISP/ISMP' 포함 데이터 필터링
    category_sheet_update(isp_url, isp_df, "ISP/ISMP")

    # 5. ISP/ISMP 및 클라우드 카테고리 공고 업데이트
    isp_cloud_url = "https://docs.google.com/spreadsheets/d/11lE8ciUVqdN97HJ__ZCRB2RV6IvNwouDv3TkuLFnyUY/edit?usp=drive_link"
    isp_cloud_df = notice_df.loc[
        (notice_df["비고"].str.contains("ISP/ISMP"))
        | (notice_df["비고"].str.contains("클라우드"))
    ]  # '비고' 컬럼에서 'ISP/ISMP' 또는 '클라우드' 포함 데이터 필터링
    category_sheet_update(isp_cloud_url, isp_cloud_df, "ISP/ISMP, 클라우드")

except (KeyboardInterrupt, SystemExit):
    # 사용자 중단 또는 시스템 종료 시 로그 기록
    print("notice check shut down.")

finally:
    # GitHub 커밋 실행 및 공고 확인 완료 메시지 출력
    git_commit()
    print("공고 확인 완료!")
