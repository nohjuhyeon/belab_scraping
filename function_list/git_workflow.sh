#!/bin/bash

# .env 파일 로드
if [ -f .env ]; then
    echo ".env 파일을 로드합니다..."
    export $(grep -v '^#' .env | xargs)
else
    echo ".env 파일을 찾을 수 없습니다. 스크립트를 종료합니다."
    exit 1
fi

# 사용법 출력
if [ $# -eq 0 ]; then
    echo "사용법: $0 '커밋 메시지'"
    exit 1
fi

# 커밋 메시지
COMMIT_MESSAGE="$1"

# 로그 파일 경로 설정
FILE_PATH=${folder_path}
LOG_FILE="$FILE_PATH/log_list/git_commit.txt"

# GitHub 사용자 정보 (환경 변수에서 가져오기)
GITHUB_USERNAME=${GITHUB_USERNAME}
GITHUB_EMAIL=${GITHUB_EMAIL}
GITHUB_TOKEN=${GITHUB_TOKEN}

# Git 사용자 정보 설정
git config --global user.email "$GITHUB_EMAIL"
git config --global user.name "$GITHUB_USERNAME"

# 변경 사항 스테이징
echo "변경 사항을 스테이지에 추가합니다..." 
git add . 2>&1

# 커밋 생성
echo "커밋을 생성합니다..."
git commit -m "$COMMIT_MESSAGE" 2>&1

# 원격 저장소에서 최신 변경 사항 가져오기
echo "원격 저장소에서 변경 사항을 가져옵니다..."
git pull 2>&1

# 변경 사항 푸쉬
echo "변경 사항을 원격 저장소에 푸쉬합니다..."
git push https://$GITHUB_USERNAME:$GITHUB_TOKEN@github.com/nohjuhyeon/belab_scraping.git 2>&1

# 로그에 완료 메시지 추가
echo "작업이 완료되었습니다!"
echo "=== Git 작업 종료: $(date) ==="
