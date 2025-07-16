#!/usr/bin/env python3
"""
영어 단어 시험 프로그램 설정 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """필요한 패키지들을 설치합니다."""
    print("필요한 패키지들을 설치하는 중...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 패키지 설치가 완료되었습니다.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 실패: {e}")
        return False

def setup_environment():
    """환경을 설정합니다."""
    print("\n환경 설정을 시작합니다...")
    
    # 필요한 디렉토리 생성
    directories = ["words", "results", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 {directory} 디렉토리 생성 완료")
    
    # .env 파일 생성 (API 키가 없는 경우)
    env_file = Path(".env")
    if not env_file.exists():
        api_key = input("\nOpenAI API 키를 입력하세요 (나중에 설정하려면 Enter): ").strip()
        if api_key:
            with open(env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            print("✅ API 키가 설정되었습니다.")
        else:
            print("⚠️  API 키는 나중에 프로그램 설정에서 설정할 수 있습니다.")
    
    print("✅ 환경 설정이 완료되었습니다.")

def create_sample_word_file():
    """샘플 단어 파일을 생성합니다."""
    sample_file = Path("words/sample.md")
    if not sample_file.exists():
        sample_content = """# 샘플 영어 단어

| 영어 | 한국어 |
|------|--------|
| apple | 사과 |
| book | 책 |
| computer | 컴퓨터 |
| door | 문 |
| elephant | 코끼리 |
| flower | 꽃 |
| guitar | 기타 |
| house | 집 |
| internet | 인터넷 |
| jacket | 재킷 |

## 4열 형식 예시

| 영어1 | 한국어1 | 영어2 | 한국어2 |
|-------|--------|-------|--------|
| key | 열쇠 | lamp | 램프 |
| mouse | 마우스 | notebook | 노트북 |
| ocean | 바다 | piano | 피아노 |
"""
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        print(f"📝 샘플 단어 파일이 생성되었습니다: {sample_file}")

def main():
    """메인 설정 함수"""
    print("🚀 영어 단어 시험 프로그램 설정을 시작합니다.\n")
    
    # 1. 패키지 설치
    if not install_requirements():
        print("패키지 설치에 실패했습니다. 수동으로 설치해주세요:")
        print("pip install -r requirements.txt")
        return
    
    # 2. 환경 설정
    setup_environment()
    
    # 3. 샘플 파일 생성
    create_sample_word_file()
    
    print("\n🎉 설정이 완료되었습니다!")
    print("\n다음 명령어로 프로그램을 실행할 수 있습니다:")
    print("python run.py")
    print("\n또는:")
    print("python daily_word_test.py")

if __name__ == "__main__":
    main()
