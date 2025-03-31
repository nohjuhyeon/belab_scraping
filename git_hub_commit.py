import os
import subprocess
from datetime import datetime

def git_commit_and_push():
    # 환경 변수에서 폴더 경로 가져오기
    folder_path = os.environ.get("folder_path")
    if not folder_path:
        print("Error: 'folder_path' 환경 변수가 설정되지 않았습니다.")
        return

    # Git 작업을 수행하는 디렉토리로 이동
    os.chdir(folder_path)

    # Git 커밋 메시지
    commit_message = "Auto Commit."

    # 현재 시간 출력
    print(f"현재 시간: {datetime.now()}")

    try:
        # Git Pull
        print("Pulling latest changes from the remote repository...")
        subprocess.run(["git", "pull"], check=True)

        # Git Add
        print("Staging changes...")
        subprocess.run(["git", "add", "."], check=True)

        # Git Commit
        print("Committing changes...")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        # Git Push
        print("Pushing changes to the remote repository...")
        subprocess.run(["git", "push"], check=True)

        print("Pull, commit, and push complete!")
    except subprocess.CalledProcessError as e:
        # Git 명령 실행 중 오류 발생 시 메시지 출력
        print(f"An error occurred: {e}")
        print("Git 작업 중 오류가 발생했습니다.")

# 스크립트를 직접 실행할 경우 git_commit_and_push() 함수 호출
if __name__ == "__main__":
    git_commit_and_push()
