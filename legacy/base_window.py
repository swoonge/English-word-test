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
        
        # 포커스 관리 설정
        self.setup_focus_management()
    
    def setup_focus_management(self):
        """창 포커스 관리를 설정합니다."""
        # 창이 활성화될 때 자동으로 포커스 설정
        self.root.bind("<FocusIn>", self.on_window_focus)
        self.root.bind("<Button-1>", self.on_window_click)
        self.root.bind("<Map>", self.on_window_map)
        
        # 창이 맨 앞으로 올 때도 포커스 설정
        self.root.lift()
        self.root.focus_force()
        
    def on_window_focus(self, event=None):
        """창이 포커스를 받을 때 호출됩니다."""
        try:
            if event and event.widget == self.root:
                self.root.focus_force()
                logger.debug(f"{self.root.title()} 창이 포커스를 받았습니다.")
        except Exception as e:
            logger.debug(f"포커스 설정 중 오류: {e}")
    
    def on_window_click(self, event=None):
        """창을 클릭할 때 호출됩니다."""
        try:
            self.root.focus_force()
            logger.debug(f"{self.root.title()} 창이 클릭되었습니다.")
        except Exception as e:
            logger.debug(f"클릭 포커스 설정 중 오류: {e}")
    
    def on_window_map(self, event=None):
        """창이 표시될 때 호출됩니다."""
        try:
            if event and event.widget == self.root:
                self.root.after(100, lambda: self.root.focus_force())
                logger.debug(f"{self.root.title()} 창이 표시되었습니다.")
        except Exception as e:
            logger.debug(f"맵 포커스 설정 중 오류: {e}")
    
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
            "highlightthickness": 0,
            "highlightcolor": self.theme.get_color("btn_bg"),  # 포커스 시 하이라이트 색상
            "highlightbackground": self.theme.get_color("btn_bg"),  # 포커스 아웃 시 하이라이트 색상
            "disabledforeground": self.theme.get_color("btn_fg"),  # 비활성화 시 글자 색상
            "takefocus": False  # 키보드 포커스 받지 않음
        }
        default_style.update(kwargs)
        button = tk.Button(parent, text=text, command=command, **default_style)
        
        # 포커스 이벤트 바인딩으로 스타일 유지
        button.bind("<FocusIn>", lambda e: self._on_button_focus_in(button))
        button.bind("<FocusOut>", lambda e: self._on_button_focus_out(button))
        
        return button
    
    def _on_button_focus_in(self, button):
        """버튼이 포커스를 받을 때 스타일 유지"""
        try:
            current_bg = button.cget("bg")
            current_fg = button.cget("fg")
            # 포커스를 받아도 현재 색상 유지
            button.configure(bg=current_bg, fg=current_fg)
        except Exception as e:
            logger.debug(f"버튼 포커스 인 스타일 설정 중 오류: {e}")
    
    def _on_button_focus_out(self, button):
        """버튼이 포커스를 잃을 때 스타일 유지"""
        try:
            current_bg = button.cget("bg")
            current_fg = button.cget("fg")
            # 포커스를 잃어도 현재 색상 유지
            button.configure(bg=current_bg, fg=current_fg)
        except Exception as e:
            logger.debug(f"버튼 포커스 아웃 스타일 설정 중 오류: {e}")
    
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
        """기본 Entry 위젯을 생성합니다 (정석 방식)."""
        # 기본 스타일만 적용 - 복잡한 테마 제거
        default_style = {
            "font": (self.font_family, self.font_size),
            "width": 30,
        }
        default_style.update(kwargs)
        
        # 기본 tkinter Entry 생성 (테마 색상 없이)
        entry = tk.Entry(parent, **default_style)
        return entry
    
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
