#!/bin/bash

# 단어시험 프로그램 실행 스크립트
# 이 스크립트는 영어 단어 시험 프로그램을 실행합니다.

# 스크립트가 있는 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Python 가상환경이 있다면 활성화 (선택사항)
# source venv/bin/activate

# 프로그램 실행
echo "영어 단어 시험 프로그램을 시작합니다..."
python3 main.py

# 프로그램 종료 후 메시지
echo "프로그램이 종료되었습니다."
