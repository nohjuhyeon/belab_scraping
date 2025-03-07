import os
import subprocess
from datetime import datetime

def git_commit():
    folder_path = os.environ.get("folder_path")
    script_path = folder_path+"function_list/git_workflow.sh"
    argument = "Auto Commit."
    print(datetime.now())

    try:
        # 스크립트 실행
        result = subprocess.run(
            [script_path, argument],
            capture_output=True,  # 표준 출력과 표준 오류를 캡처
            text=True,            # 출력을 문자열로 처리
            check=True            # 명령어 실패 시 예외 발생
        )
        # 실행 결과 출력
        print("commit complete!")
    except subprocess.CalledProcessError as e:
        # 오류 발생 시 출력
        print("An error occurred while executing the script.")

if __name__ == "__main__":
    git_commit()
