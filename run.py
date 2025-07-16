#!/usr/bin/env python3
"""
영어 단어 시험 프로그램 실행 스크립트 (호환성 유지)
새로운 모듈화된 구조로 리디렉션
"""

import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    print("🔄 새로운 모듈화된 구조로 실행 중...")
    print("앞으로는 'python main.py'를 사용하는 것을 권장합니다.")
    print("-" * 50)
    
    # 새로운 main.py로 리디렉션
    import main
    main.main()
    
except ImportError as e:
    print(f"모듈 import 오류: {e}")
    print("필요한 패키지를 설치해주세요: pip install -r requirements.txt")
    print("또는 필요한 파일들이 있는지 확인하세요:")
    print("- main.py")
    print("- src/ 디렉토리와 하위 모듈들")
except Exception as e:
    print(f"프로그램 실행 오류: {e}")
    input("Press Enter to exit...")
