#!/bin/bash

# .env 파일 로드 (선택 사항)
if [ -f .env ]; then
    echo ".env 파일을 로드합니다..."
    export $(grep -v '^#' /app/belab_scraping/.env | xargs)
else
    echo ".env 파일을 찾을 수 없습니다. 스크립트를 종료합니다."
    exit 1
fi

# 사용법 출력
if [ $# -lt 4 ]; then
    echo "사용법: $0 '커밋 메시지'"
    exit 1
fi

# 인자로 받은 값 저장
COMMIT_MESSAGE="$1"
FOLDER_PATH="$2"
GITHUB_USERNAME="$3"
GITHUB_EMAIL="$4"
GITHUB_TOKEN="$5"

# 로그 파일 경로 설정
LOG_FILE="$FOLDER_PATH/log_list/git_commit.txt"

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
