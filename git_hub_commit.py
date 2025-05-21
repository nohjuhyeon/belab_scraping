import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(dotenv_path='/app/belab_scraping/.env')

def git_commit():
    # 환경 변수에서 필요한 값 가져오기
    folder_path = os.environ.get("folder_path")
    commit_message = "Auto Commit."
    github_username = os.environ.get("GITHUB_USERNAME")
    github_email = os.environ.get("GITHUB_EMAIL")
    github_token = os.environ.get("GH_TOKEN")
    log_file_path = os.path.join(folder_path, "log_list/git_commit.txt")

    print(f"현재 시간: {datetime.now()}")

    # 작업 디렉토리 변경
    os.chdir(folder_path)

    # .git 디렉토리 확인
    if '.git' not in os.listdir(folder_path):
        print(".git 디렉토리가 없습니다. Git 저장소가 아닙니다.")
        return

    try:
        # Git 사용자 정보 설정
        subprocess.run(['git', 'config', '--global', 'user.email', github_email], check=True)
        subprocess.run(['git', 'config', '--global', 'user.name', github_username], check=True)

        # Git 상태 확인
        print("현재 Git 상태를 확인합니다...")
        status_result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        print(status_result.stdout)

        # 변경 사항이 없으면 커밋 단계를 생략
        if "nothing to commit, working tree clean" in status_result.stdout:
            print("변경 사항이 없으므로 커밋 단계를 건너뜁니다.")
        else:
            # 변경 사항 스테이징
            print("변경 사항을 스테이지에 추가합니다...")
            subprocess.run(['git', 'add', '.'], check=True)

            # 커밋 생성
            print("커밋을 생성합니다...")
            commit_message = f"자동 커밋: {datetime.now()}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)

        # 원격 저장소에서 최신 변경 사항 가져오기
        print("원격 저장소에서 변경 사항을 가져옵니다...")
        subprocess.run(['git', 'pull', '--rebase'], check=True)

        # 변경 사항 푸쉬
        print("변경 사항을 원격 저장소에 푸쉬합니다...")
        remote_url = f"https://{github_username}:{github_token}@github.com/{github_username}/belab_scraping.git"
        subprocess.run(['git', 'push', remote_url], check=True)

        # 로그에 완료 메시지 추가
        with open(log_file_path, "a") as log_file:
            log_file.write(f"=== Git 작업 종료: {datetime.now()} ===\n")

        print("작업이 완료되었습니다!")

    except subprocess.CalledProcessError as e:
        print("작업 중 오류가 발생했습니다.")
        with open(log_file_path, "a") as log_file:
            log_file.write(f"=== Git 작업 실패: {datetime.now()} ===\n")

if __name__ == "__main__":
    git_commit()
