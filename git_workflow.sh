#!/bin/bash

# 사용법 출력
if [ $# -eq 0 ]; then
    echo "사용법: $0 '커밋 메시지'"
    exit 1
fi

# 커밋 메시지
COMMIT_MESSAGE="$1"

# .env 파일에서 GitHub 사용자 정보 가져오기
GITHUB_USERNAME=${GITHUB_USERNAME}
GITHUB_EMAIL=${GITHUB_EMAIL}
GITHUB_TOKEN=${GITHUB_TOKEN}

# Git 사용자 정보 설정
git config --global user.email "njh2720@gmail.com"
git config --global user.name "nohjuhyeon"

echo "변경 사항을 스테이지에 추가합니다..."
git add .

echo "커밋을 생성합니다..."
git commit -m "$COMMIT_MESSAGE"


git push

echo "작업이 완료되었습니다!"
