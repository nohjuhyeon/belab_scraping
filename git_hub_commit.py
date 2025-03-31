import os
import subprocess
from datetime import datetime

def git_commit():
    # 환경 변수에서 폴더 경로 가져오기
    folder_path = os.environ.get("folder_path")
    # Git 작업을 수행하는 스크립트 경로 설정
    script_path = folder_path + "function_list/git_workflow.sh"
    # Git 커밋 메시지
    argument = "Auto Commit."
    
    # 현재 시간 출력
    print(datetime.now())

    try:
        # 스크립트 실행
        result = subprocess.run(
            [script_path, argument],  # 실행할 스크립트와 인자
            capture_output=True,      # 표준 출력과 표준 오류 캡처
            text=True,                # 출력을 문자열로 처리
            check=True                # 명령 실행 실패 시 예외 발생
        )
        # 스크립트 실행 성공 메시지 출력
        print("commit complete!")
    except subprocess.CalledProcessError as e:
        # 스크립트 실행 중 오류 발생 시 메시지 출력
        print("An error occurred while executing the script.")

# 스크립트를 직접 실행할 경우 git_commit() 함수 호출
if __name__ == "__main__":
    git_commit()
