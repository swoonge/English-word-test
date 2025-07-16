"""
UI 테마 관리 유틸리티
"""


class ThemeManager:
    """테마 관리 클래스"""
    
    THEMES = {
        "dark": {
            "bg": "#23272e",
            "fg": "#f5f6fa",
            "btn_bg": "#444c56",
            "btn_fg": "#f5f6fa",
            "btn_active_bg": "#5d646f",  # 버튼 활성화 시 배경색
            "btn_active_fg": "#ffffff",   # 버튼 활성화 시 글자색
            "entry_bg": "#ffffff",        # 입력 필드 배경 (흰색으로 명확하게)
            "entry_fg": "#000000",        # 입력 필드 글자 (검은색으로 명확하게)
            "highlight": "#2986cc",
            "success": "#4caf50",
            "error": "#f44336"
        },
        "light": {
            "bg": "#ffffff",
            "fg": "#333333",
            "btn_bg": "#e0e0e0",
            "btn_fg": "#333333",
            "btn_active_bg": "#d0d0d0",  # 버튼 활성화 시 배경색
            "btn_active_fg": "#000000",   # 버튼 활성화 시 글자색
            "entry_bg": "#ffffff",        # 입력 필드 배경
            "entry_fg": "#000000",        # 입력 필드 글자 (검은색으로 명확하게)
            "highlight": "#2986cc",
            "success": "#4caf50",
            "error": "#f44336"
        }
    }
    
    def __init__(self, theme_name: str = "dark"):
        self.current_theme = self.THEMES.get(theme_name, self.THEMES["dark"])
        self.theme_name = theme_name
    
    def set_theme(self, theme_name: str):
        """테마를 변경합니다."""
        if theme_name in self.THEMES:
            self.theme_name = theme_name
            self.current_theme = self.THEMES[theme_name]
    
    def get_theme_name(self) -> str:
        """현재 테마 이름을 반환합니다."""
        return self.theme_name
    
    def get_color(self, key: str) -> str:
        """테마 색상을 가져옵니다."""
        return self.current_theme.get(key, "#000000")
