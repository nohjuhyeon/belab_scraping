#!/bin/bash

# .env 파일 로드 (환경 변수를 불러오는 단계 - 현재는 구현되지 않음)

# 사용법 출력
if [ $# -eq 0 ]; then
    # 인자가 없는 경우 사용법 안내 메시지 출력
    echo "사용법: $0 '커밋 메시지'"
    exit 1
fi

# 커밋 메시지 설정
COMMIT_MESSAGE="$1"  # 첫 번째 인자를 커밋 메시지로 설정

# 작업 디렉토리로 이동
cd ${folder_path} || exit  # 폴더 경로로 이동, 실패 시 스크립트 종료

# .env 파일에서 GitHub 사용자 정보 가져오기 (현재 변수는 스크립트 내에서 직접 설정됨)
GITHUB_USERNAME=${GITHUB_USERNAME}  # GitHub 사용자 이름
GITHUB_EMAIL=${GITHUB_EMAIL}        # GitHub 이메일 주소
GITHUB_TOKEN=${GITHUB_TOKEN}        # GitHub Personal Access Token

# Git 사용자 정보 설정
git config --global user.email "njh2720@gmail.com"  # 사용자 이메일 설정
git config --global user.name "nohjuhyeon"         # 사용자 이름 설정

# 변경 사항 스테이징
echo "변경 사항을 스테이지에 추가합니다..."
git add .  # 모든 변경 사항을 스테이징

# 커밋 생성
echo "커밋을 생성합니다..."
git commit -m "$COMMIT_MESSAGE"  # 커밋 메시지를 사용하여 커밋 생성

# 최신 변경 사항 가져오기
git pull  # 원격 저장소의 최신 변경 사항을 로컬로 가져옴

# 변경 사항 푸시
echo "변경 사항을 원격 저장소로 푸시합니다..."
git push https://"$GITHUB_USERNAME":"$GITHUB_TOKEN"@github.com/nohjuhyeon/belab_scraping.git
# Personal Access Token을 사용하여 변경 사항을 원격 저장소로 푸시

# 작업 완료 메시지 출력
echo "작업이 완료되었습니다!"
