import os
import subprocess
import sys

# MeCab 경로 설정
BASE_DIR = "/mecab-ko-dic-2.1.1-20180720"
USER_DIC = os.path.join(BASE_DIR, "user-dic/user-nnp.csv")
ADD_USERDIC_SCRIPT = os.path.join(BASE_DIR, "tools/add-userdic.sh")

def main(entry):
    # BASE_DIR 존재 여부 확인
    if not os.path.exists(BASE_DIR):
        print(f"Error: Base directory {BASE_DIR} does not exist.")
        sys.exit(1)

    # user-nnp.csv 파일에 항목 추가
    try:
        with open(USER_DIC, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"Added entry to {USER_DIC}: {entry}")
    except Exception as e:
        print(f"Error writing to {USER_DIC}: {e}")
        sys.exit(1)

    # add-userdic.sh 실행
    if os.path.exists(ADD_USERDIC_SCRIPT) and os.access(ADD_USERDIC_SCRIPT, os.X_OK):
        try:
            subprocess.run([ADD_USERDIC_SCRIPT], check=True)
            print(f"Executed {ADD_USERDIC_SCRIPT}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {ADD_USERDIC_SCRIPT}: {e}")
            sys.exit(1)
    else:
        print(f"Error: {ADD_USERDIC_SCRIPT} not found or not executable.")
        sys.exit(1)

    # make install 실행
    try:
        subprocess.run(["make", "install"], cwd=BASE_DIR, check=True)
        print("make install completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during make install: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 입력값 확인
    print("단어 추가를 위한 정보를 입력하세요.")
    print("형식: 단어 품사 중요도 (예: 서울 NNP 10)")
    
    while True:
        try:
            user_input = input("입력: ").strip()
            if not user_input:
                print("입력이 비어 있습니다. 다시 시도하세요.")
                continue

            # 입력값 파싱
            parts = user_input.split()
            if len(parts) != 3:
                print("올바른 형식으로 입력하세요: 단어 품사 중요도")
                continue

            word, pos, score = parts
            pos = pos.upper()  # 품사는 대문자로 변환 (예: NNP)
            
            # 기본값 검증 (필요 시 추가 검증 가능)
            if not score.isdigit():
                print("중요도는 숫자로 입력해야 합니다.")
                continue

            # 사전 항목 생성
            line = f"{word},,,{score},{pos},*,F,{word},*,*,*,*\n"
            main(line)
            break  # 성공적으로 처리되면 루프 종료
        except KeyboardInterrupt:
            print("\n사용자가 작업을 취소했습니다.")
            sys.exit(0)