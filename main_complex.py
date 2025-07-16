#!/usr/bin/env python3
"""
영어 단어 시험 프로그램 v2.0
메인 진입점
"""
import os
import sys
import logging

# 현재 스크립트의 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 환경 변수 로딩
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 로깅 설정
def setup_logging():
    """로깅을 설정합니다."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'word_test.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    """메인 함수"""
    try:
        # 로깅 설정
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("영어 단어 시험 프로그램 v2.0 시작")
        
        # 메인 애플리케이션 실행
        from src.ui.main_window import MainApplication
        app = MainApplication()
        app.run()
        
        logger.info("프로그램 정상 종료")
        
    except ImportError as e:
        print(f"모듈 임포트 오류: {e}")
        print("필요한 패키지가 설치되어 있는지 확인하세요.")
        print("pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        if logging.getLogger().hasHandlers():
            logging.error(f"프로그램 실행 중 오류: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
