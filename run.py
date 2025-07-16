#!/usr/bin/env python3
"""
영어 단어 시험 프로그램 실행 스크립트
"""

import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from daily_word_test import main
    main()
except ImportError as e:
    print(f"모듈 import 오류: {e}")
    print("필요한 패키지를 설치해주세요: pip install -r requirements.txt")
except Exception as e:
    print(f"프로그램 실행 오류: {e}")
    input("Press Enter to exit...")
