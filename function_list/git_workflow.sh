#!/bin/bash

# .env 파일 로드
# .env 파일이 있다면 여기에 추가로 로드하는 코드를 작성할 수 있습니다.

# 사용법 출력
if [ $# -eq 0 ]; then
    echo "사용법: $0 '커밋 메시지'"
    exit 1
fi

# 커밋 메시지
COMMIT_MESSAGE="$1"
FILE_PATH="$2"
GITHUB_USERNAME="$3"
GITHUB_EMAIL="$4"
GH_TOKEN="$5"

LOG_FILE="$FILE_PATH/log_list/git_commit.txt"


# Git 사용자 정보 설정
git config --global user.email "njh2720@gmail.com"
git config --global user.name "nohjuhyeon"


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
git push https://$GITHUB_USERNAME:$GH_TOKEN@github.com/nohjuhyeon/belab_scraping.git 2>&1

# 로그에 완료 메시지 추가
echo "작업이 완료되었습니다!"
echo "=== Git 작업 종료: $(date) ==="
