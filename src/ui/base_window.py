"""
기본 UI 윈도우 클래스
"""
import tkinter as tk
from tkinter import messagebox
import logging

from ..core.config import Config
from ..utils.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class BaseWindow:
    """기본 윈도우 클래스"""
    
    def __init__(self, config: Config, title: str, geometry: str = None):
        self.config = config
        self.theme = ThemeManager(config.get("ui.theme", "dark"))
        self.root = tk.Tk()
        self.root.title(title)
        if geometry:
            self.root.geometry(geometry)
        self.root.configure(bg=self.theme.get_color("bg"))
        
        # 폰트 설정
        self.font_family = config.get("ui.font_family", "Arial")
        self.font_size = config.get("ui.font_size", 12)
    
    def create_button(self, parent, text: str, command, **kwargs) -> tk.Button:
        """통일된 스타일의 버튼을 생성합니다."""
        default_style = {
            "bg": self.theme.get_color("btn_bg"),
            "fg": self.theme.get_color("btn_fg"),
            "activebackground": self.theme.get_color("btn_active_bg"),
            "activeforeground": self.theme.get_color("btn_active_fg"),
            "font": (self.font_family, self.font_size),
            "relief": "flat",
            "cursor": "hand2",
            "borderwidth": 0,
            "highlightthickness": 0
        }
        default_style.update(kwargs)
        return tk.Button(parent, text=text, command=command, **default_style)
    
    def create_label(self, parent, text: str, **kwargs) -> tk.Label:
        """통일된 스타일의 레이블을 생성합니다."""
        default_style = {
            "bg": self.theme.get_color("bg"),
            "fg": self.theme.get_color("fg"),
            "font": (self.font_family, self.font_size)
        }
        default_style.update(kwargs)
        return tk.Label(parent, text=text, **default_style)
    
    def create_entry(self, parent, **kwargs) -> tk.Entry:
        """통일된 스타일의 입력 필드를 생성합니다."""
        default_style = {
            "bg": self.theme.get_color("entry_bg"),
            "fg": self.theme.get_color("entry_fg"),
            "font": (self.font_family, self.font_size),
            "relief": "flat",
            "insertbackground": self.theme.get_color("fg")
        }
        default_style.update(kwargs)
        return tk.Entry(parent, **default_style)
    
    def show_error(self, title: str, message: str):
        """에러 메시지를 표시합니다."""
        messagebox.showerror(title, message)
        logger.error(f"{title}: {message}")
    
    def show_info(self, title: str, message: str):
        """정보 메시지를 표시합니다."""
        messagebox.showinfo(title, message)
        logger.info(f"{title}: {message}")
    
    def show_warning(self, title: str, message: str):
        """경고 메시지를 표시합니다."""
        messagebox.showwarning(title, message)
        logger.warning(f"{title}: {message}")
