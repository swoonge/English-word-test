"""
시스템별 호환성 유틸리티
"""
import platform
import sys
import tkinter as tk
from tkinter import font as tkfont
import logging

logger = logging.getLogger(__name__)


class SystemCompatibility:
    """시스템별 호환성을 관리하는 클래스"""
    
    @staticmethod
    def get_system_info():
        """시스템 정보를 반환합니다."""
        return {
            'platform': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'python_version': sys.version,
            'is_linux': platform.system() == 'Linux',
            'is_windows': platform.system() == 'Windows',
            'is_macos': platform.system() == 'Darwin'
        }
    
    @staticmethod
    def get_available_fonts():
        """시스템에서 사용 가능한 폰트 목록을 반환합니다."""
        try:
            root = tk.Tk()
            root.withdraw()  # 창을 숨김
            available_fonts = list(tkfont.families())
            root.destroy()
            return sorted(available_fonts)
        except Exception as e:
            logger.error(f"폰트 목록 조회 실패: {e}")
            return []
    
    @staticmethod
    def get_recommended_font():
        """시스템별 권장 폰트를 반환합니다."""
        system_info = SystemCompatibility.get_system_info()
        available_fonts = SystemCompatibility.get_available_fonts()
        
        # 시스템별 우선순위 폰트 목록
        if system_info['is_linux']:
            font_priorities = [
                'DejaVu Sans', 'Liberation Sans', 'Ubuntu', 'Cantarell',
                'Noto Sans', 'Arial', 'Helvetica', 'sans-serif'
            ]
        elif system_info['is_windows']:
            font_priorities = [
                'Segoe UI', 'Arial', 'Helvetica', 'Calibri', 'Tahoma'
            ]
        elif system_info['is_macos']:
            font_priorities = [
                'SF Pro Text', 'Helvetica Neue', 'Arial', 'Helvetica'
            ]
        else:
            font_priorities = ['Arial', 'Helvetica', 'sans-serif']
        
        # 사용 가능한 첫 번째 폰트 반환
        for font_name in font_priorities:
            if font_name in available_fonts:
                logger.info(f"선택된 폰트: {font_name}")
                return font_name
        
        # 기본 폰트 반환
        if available_fonts:
            default_font = available_fonts[0]
            logger.warning(f"권장 폰트를 찾을 수 없어 기본 폰트 사용: {default_font}")
            return default_font
        
        logger.warning("사용 가능한 폰트가 없어 시스템 기본값 사용")
        return "TkDefaultFont"
    
    @staticmethod
    def get_recommended_font_size():
        """시스템별 권장 폰트 크기를 반환합니다."""
        system_info = SystemCompatibility.get_system_info()
        
        if system_info['is_linux']:
            return 10  # 리눅스에서는 일반적으로 작은 폰트 선호
        elif system_info['is_windows']:
            return 9   # 윈도우 기본
        elif system_info['is_macos']:
            return 13  # 맥OS는 Retina 디스플레이로 인해 큰 폰트
        else:
            return 10
    
    @staticmethod
    def check_clipboard_support():
        """클립보드 지원 여부를 확인합니다."""
        try:
            import pyperclip
            pyperclip.copy("test")
            test_text = pyperclip.paste()
            return test_text == "test"
        except Exception as e:
            logger.warning(f"클립보드 기능 확인 실패: {e}")
            return False
    
    @staticmethod
    def check_drag_drop_support():
        """드래그 앤 드롭 지원 여부를 확인합니다."""
        try:
            import tkinterdnd2
            return True
        except ImportError:
            logger.warning("tkinterdnd2가 설치되지 않아 드래그 앤 드롭 기능을 사용할 수 없습니다.")
            return False
    
    @staticmethod
    def get_theme_recommendations():
        """시스템별 테마 권장사항을 반환합니다."""
        system_info = SystemCompatibility.get_system_info()
        
        if system_info['is_linux']:
            # 리눅스는 일반적으로 다크 테마 선호
            return {
                'default_theme': 'dark',
                'supports_system_theme': True,
                'theme_notes': '우분투/GNOME 환경에서는 다크 테마가 권장됩니다.'
            }
        elif system_info['is_windows']:
            return {
                'default_theme': 'light',
                'supports_system_theme': True,
                'theme_notes': '윈도우 10/11의 시스템 테마를 따릅니다.'
            }
        elif system_info['is_macos']:
            return {
                'default_theme': 'light',
                'supports_system_theme': True,
                'theme_notes': 'macOS의 시스템 테마를 따릅니다.'
            }
        else:
            return {
                'default_theme': 'light',
                'supports_system_theme': False,
                'theme_notes': '기본 라이트 테마를 사용합니다.'
            }
    
    @staticmethod
    def print_system_report():
        """시스템 호환성 보고서를 출력합니다."""
        print("=" * 60)
        print("🖥️  시스템 호환성 보고서")
        print("=" * 60)
        
        system_info = SystemCompatibility.get_system_info()
        print(f"플랫폼: {system_info['platform']} {system_info['release']}")
        print(f"아키텍처: {system_info['machine']}")
        print(f"Python: {sys.version.split()[0]}")
        
        print("\n📝 폰트 정보:")
        recommended_font = SystemCompatibility.get_recommended_font()
        recommended_size = SystemCompatibility.get_recommended_font_size()
        print(f"권장 폰트: {recommended_font}")
        print(f"권장 크기: {recommended_size}")
        
        print("\n🔧 기능 지원:")
        clipboard_support = SystemCompatibility.check_clipboard_support()
        dnd_support = SystemCompatibility.check_drag_drop_support()
        print(f"클립보드: {'✅ 지원' if clipboard_support else '❌ 미지원'}")
        print(f"드래그 앤 드롭: {'✅ 지원' if dnd_support else '❌ 미지원'}")
        
        print("\n🎨 테마 정보:")
        theme_rec = SystemCompatibility.get_theme_recommendations()
        print(f"권장 테마: {theme_rec['default_theme']}")
        print(f"참고: {theme_rec['theme_notes']}")
        
        print("=" * 60)


if __name__ == "__main__":
    # 테스트 실행
    SystemCompatibility.print_system_report()
