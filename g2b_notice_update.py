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
from dotenv import load_dotenv
loaded = load_dotenv(dotenv_path='/app/belab_scraping/.env')

try:
    # GitHub 커밋 실행
    git_commit()

    # 공고 확인 프로세스 시작 로그
    print("----------------공고 확인 시작----------------")
    print(datetime.now())

    # 로그 파일 설정
    folder_path = os.environ.get("folder_path")  # 환경 변수에서 폴더 경로 가져오기
    print(folder_path)

    # 나라장터 데이터 수집 시작
    print("나라장터 공고를 찾습니다.")
    mongo_client,collection = mongo_setting("news_scraping", "notice_list")  # MongoDB 설정
    results = collection.find({}, {"_id": 0})  # MongoDB에서 기존 공고 데이터 가져오기
    existing_df = [i for i in results]  # 결과를 리스트로 변환
    existing_df = pd.DataFrame(existing_df)  # DataFrame으로 변환
    mongo_client.close()

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
    ai_url = "https://docs.google.com/spreadsheets/d/1Rd6o2rBays25jvcz6SGf03Pvr3ci5epfzlI2TmvWTQI/edit?usp=sharing"
    ai_df = notice_df.loc[
        notice_df["비고"].str.contains("인공지능")
    ]  # '비고' 컬럼에서 '인공지능' 포함 데이터 필터링
    category_sheet_update(ai_url, ai_df, "인공지능")

    # 2. 데이터 카테고리 공고 업데이트
    data_url = "https://docs.google.com/spreadsheets/d/1tTaqo_BPZvHEKx_OcFOj3RoFr-e_9i5-ftPW4hS4Qq0/edit?usp=sharing"
    data_df = notice_df.loc[
        notice_df["비고"].str.contains("데이터베이스")
    ]  # '비고' 컬럼에서 '데이터' 포함 데이터 필터링
    category_sheet_update(data_url, data_df, "데이터베이스")

    # 3. 클라우드 카테고리 공고 업데이트
    cloud_url = "https://docs.google.com/spreadsheets/d/1YJI1NrcLaHiTtyjhK071MiIYQ36G0LWJ4QSfgE67paU/edit?usp=sharing"
    cloud_df = notice_df.loc[
        notice_df["비고"].str.contains("클라우드 컴퓨팅")
    ]  # '비고' 컬럼에서 '클라우드' 포함 데이터 필터링
    category_sheet_update(cloud_url, cloud_df, "클라우드 컴퓨팅")

    # 4. 네트워크/보안 카테고리 공고 업데이트
    network_security_url = "https://docs.google.com/spreadsheets/d/12aoE7vXB7JNICh93q0NaabCdF8wsLiBEX8WN8fiZDxI/edit?usp=sharing"
    network_security_df = notice_df.loc[
        notice_df["비고"].str.contains("네트워크 및 보안")
    ]  # '비고' 컬럼에서 '클라우드' 포함 데이터 필터링
    category_sheet_update(network_security_url, network_security_df, "네트워크 및 보안")

    # 5. AR/VR 및 메타버스 카테고리 공고 업데이트
    metaverse_url = "https://docs.google.com/spreadsheets/d/1X5i6DflM_ZBE_SK4uEe2hhw-f6F1ZGr_4akRDcrGW4Q/edit?usp=sharing"
    metaverse_df = notice_df.loc[
        notice_df["비고"].str.contains("AR/VR 및 메타버스")
    ]  # '비고' 컬럼에서 '클라우드' 포함 데이터 필터링
    category_sheet_update(metaverse_url, metaverse_df, "AR/VR 및 메타버스")

    # 6. 소프트웨어 개발 및 관리 카테고리 공고 업데이트
    software_url = "https://docs.google.com/spreadsheets/d/1jL5PAmWhI5Uv3Va5oW6zhbumfemHQzCqoOGUZnfujf8/edit?usp=sharing"
    software_df = notice_df.loc[
        notice_df["비고"].str.contains("소프트웨어 개발 및 관리")
    ]  # '비고' 컬럼에서 '클라우드' 포함 데이터 필터링
    category_sheet_update(software_url, software_df, "소프트웨어 개발 및 관리")

    # 7. 블록체인 카테고리 공고 업데이트
    blockchain_url = "https://docs.google.com/spreadsheets/d/1V4LvEm_nI8iOy0784WMDERB-ENLbMJeQ1U3uTvgmEcU/edit?usp=sharing"
    blockchain_df = notice_df.loc[
        notice_df["비고"].str.contains("블록체인")
    ]  # '비고' 컬럼에서 '클라우드' 포함 데이터 필터링
    category_sheet_update(blockchain_url, blockchain_df, "블록체인")

    # 8. IoT 카테고리 공고 업데이트
    IoT_url = "https://docs.google.com/spreadsheets/d/19aYGVI6FIbyfQf9zyEqqpi8EeITo2WCVWNRT-o1V3o4/edit?usp=sharing"
    IoT_df = notice_df.loc[
        notice_df["비고"].str.contains("IoT")
    ]  # '비고' 컬럼에서 '클라우드' 포함 데이터 필터링
    category_sheet_update(IoT_url, IoT_df, "IoT")

    # 9. ISP/ISMP 카테고리 공고 업데이트
    isp_url = "https://docs.google.com/spreadsheets/d/1aI9VKVjoLQ2g6-yOnq4VCozswvzQchVJD1VrHP4wKdw/edit?usp=sharing"
    isp_df = notice_df.loc[
        notice_df["비고"].str.contains("ISP/ISMP")
    ]  # '비고' 컬럼에서 'ISP/ISMP' 포함 데이터 필터링
    category_sheet_update(isp_url, isp_df, "ISP/ISMP")

except (KeyboardInterrupt, SystemExit):
    # 사용자 중단 또는 시스템 종료 시 로그 기록
    print("The notice check cannot be finished due to an error.")

finally:
    # GitHub 커밋 실행 및 공고 확인 완료 메시지 출력
    git_commit()
    print("공고 확인 완료!")
