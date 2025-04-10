#!/bin/bash

# 사용법 출력
if [ $# -lt 5 ]; then
    echo "사용법: $0 '커밋 메시지' '파일 경로' 'GitHub 사용자 이름' 'GitHub 이메일' 'GitHub 토큰'"
    exit 1
fi

# 인자 값 설정
COMMIT_MESSAGE="$1"
FILE_PATH="$2"
GITHUB_USERNAME="$3"
GITHUB_EMAIL="$4"
GH_TOKEN="$5"

# 로그 파일 경로 설정
LOG_FILE="$FILE_PATH/log_list/git_commit.txt"

# Git 사용자 정보 설정
echo "Git 사용자 정보를 설정합니다..."
git config --global user.email "$GITHUB_EMAIL"
git config --global user.name "$GITHUB_USERNAME"

# 변경 사항 스테이징
echo "변경 사항을 스테이지에 추가합니다..."
git add . 2>&1
if [ $? -ne 0 ]; then
    echo "변경 사항을 추가하는 중 오류가 발생했습니다."
    exit 1
fi

# 커밋 생성
echo "커밋을 생성합니다..."
git commit -m "$COMMIT_MESSAGE" 2>&1
if [ $? -ne 0 ]; then
    echo "커밋 생성 중 오류가 발생했습니다. (변경 사항이 없을 수도 있습니다.)"
    exit 1
fi

# 원격 저장소에서 최신 변경 사항 가져오기
echo "원격 저장소에서 변경 사항을 가져옵니다..."
git pull --rebase 2>&1
if [ $? -ne 0 ]; then
    echo "원격 변경 사항을 가져오는 중 오류가 발생했습니다."
    exit 1
fi

# 변경 사항 푸쉬
echo "변경 사항을 원격 저장소에 푸쉬합니다..."
git push https://$GITHUB_USERNAME:$GH_TOKEN@github.com/$GITHUB_USERNAME/belab_scraping.git 2>&1
if [ $? -ne 0 ]; then
    echo "변경 사항을 푸쉬하는 중 오류가 발생했습니다."
    exit 1
fi

# 로그에 완료 메시지 추가
echo "작업이 완료되었습니다!"
echo "=== Git 작업 종료: $(date) ===" >> "$LOG_FILE"
