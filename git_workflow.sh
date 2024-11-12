#!/bin/bash

# .env 파일 로드
source .env

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

# 토큰을 사용하여 push - 수정된 URL 사용 및 브랜치 명시
git remote add origin https://github.com/nohjuhyeon/belab_scraping.git

git push https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/nohjuhyeon/belab_scraping.git

# 보안을 위해 토큰이 포함된 URL 제거 (선택 사항 - 방법 1)

echo "작업이 완료되었습니다!"
