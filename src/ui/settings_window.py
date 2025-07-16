"""
설정 창 UI
"""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import logging
from openai import OpenAI

from .base_window import BaseWindow
from ..core.config import Config

logger = logging.getLogger(__name__)


class SettingsWindow(BaseWindow):
    """설정 창 클래스"""
    
    def __init__(self, config: Config, callback=None):
        # BaseWindow 초기화를 우선 하지 않고, 직접 설정
        self.config = config
        from ..utils.theme_manager import ThemeManager
        self.theme = ThemeManager(config.get("ui.theme", "dark"))
        
        # Toplevel 창 생성 (별도 창)
        self.root = tk.Toplevel()
        self.root.title("설정")
        self.root.geometry("500x450")
        self.root.configure(bg=self.theme.get_color("bg"))
        
        # 폰트 설정
        self.font_family = config.get("ui.font_family", "Arial")
        self.font_size = config.get("ui.font_size", 12)
        
        # 설정 창 특별 설정
        self.setup_settings_window()
        
        self.callback = callback
        self.setup_ui()
        self.load_current_settings()
    
    def setup_settings_window(self):
        """설정 창 특별 설정을 적용합니다."""
        # 항상 맨 앞에 표시
        self.root.transient()
        self.root.grab_set()  # 모달 창으로 설정
        
        # 포커스 관리
        self.root.lift()
        self.root.focus_force()
        
        # 창 활성화 이벤트 바인딩
        self.root.bind("<FocusIn>", self.on_settings_focus)
        self.root.bind("<Button-1>", self.on_settings_click)
        self.root.bind("<Map>", self.on_settings_map)
        
        # 창을 화면 중앙에 배치
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (450 // 2)
        self.root.geometry(f"500x450+{x}+{y}")
        
    def on_settings_focus(self, event=None):
        """설정 창이 포커스를 받을 때 호출됩니다."""
        try:
            self.root.focus_force()
            logger.debug("설정 창이 포커스를 받았습니다.")
        except Exception as e:
            logger.debug(f"설정 창 포커스 설정 중 오류: {e}")
    
    def on_settings_click(self, event=None):
        """설정 창을 클릭할 때 호출됩니다."""
        try:
            self.root.focus_force()
            logger.debug("설정 창이 클릭되었습니다.")
        except Exception as e:
            logger.debug(f"설정 창 클릭 포커스 설정 중 오류: {e}")
    
    def on_settings_map(self, event=None):
        """설정 창이 표시될 때 호출됩니다."""
        try:
            self.root.after(100, lambda: self.root.focus_force())
            logger.debug("설정 창이 표시되었습니다.")
        except Exception as e:
            logger.debug(f"설정 창 맵 포커스 설정 중 오류: {e}")
    
    def setup_ui(self):
        """설정 UI를 구성합니다."""
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg=self.theme.get_color("bg"))
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # OpenAI API 키 설정
        api_frame = tk.LabelFrame(main_frame, text="OpenAI 설정", 
                                  bg=self.theme.get_color("bg"), 
                                  fg=self.theme.get_color("fg"))
        api_frame.pack(fill="x", pady=(0, 10))
        
        self.create_label(api_frame, "API 키:").pack(anchor="w", padx=10, pady=5)
        api_key_frame = tk.Frame(api_frame, bg=self.theme.get_color("bg"))
        api_key_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.api_key_entry = self.create_entry(api_key_frame, show="*", width=35)
        self.api_key_entry.pack(side="left", fill="x", expand=True)
        
        self.create_button(api_key_frame, "테스트", self.test_api_key, width=8).pack(side="right", padx=(5, 0))
        
        # UI 설정
        ui_frame = tk.LabelFrame(main_frame, text="UI 설정",
                                 bg=self.theme.get_color("bg"),
                                 fg=self.theme.get_color("fg"))
        ui_frame.pack(fill="x", pady=(0, 10))
        
        # 테마 선택 (스위치 형태)
        theme_frame = tk.Frame(ui_frame, bg=self.theme.get_color("bg"))
        theme_frame.pack(fill="x", padx=10, pady=5)
        
        self.create_label(theme_frame, "테마:").pack(anchor="w", pady=(0, 5))
        
        # 테마 스위치 컨테이너
        switch_container = tk.Frame(theme_frame, bg=self.theme.get_color("bg"))
        switch_container.pack(anchor="w", pady=(0, 10))
        
        # 현재 테마 상태를 저장할 변수
        self.current_theme = tk.StringVar()
        
        # Dark 테마 버튼
        self.dark_btn = self.create_button(switch_container, "🌙 Dark", 
                                         lambda: self.switch_theme("dark"),
                                         width=10)
        self.dark_btn.pack(side="left", padx=(0, 2))
        
        # Light 테마 버튼  
        self.light_btn = self.create_button(switch_container, "☀️ Light",
                                          lambda: self.switch_theme("light"), 
                                          width=10)
        self.light_btn.pack(side="left", padx=(2, 0))
        
        # 현재 선택된 테마 표시 라벨
        self.theme_status_label = self.create_label(switch_container, "",
                                                   font=(self.font_family, 9),
                                                   fg=self.theme.get_color("highlight"))
        self.theme_status_label.pack(side="left", padx=(10, 0))
        
        # 폴더 설정
        folder_frame = tk.LabelFrame(main_frame, text="폴더 설정",
                                    bg=self.theme.get_color("bg"),
                                    fg=self.theme.get_color("fg"))
        folder_frame.pack(fill="x", pady=(0, 10))
        
        # 단어 파일 폴더
        self.create_label(folder_frame, "단어 파일 폴더:").pack(anchor="w", padx=10, pady=5)
        words_folder_frame = tk.Frame(folder_frame, bg=self.theme.get_color("bg"))
        words_folder_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.words_folder_var = tk.StringVar()
        self.words_folder_entry = self.create_entry(words_folder_frame, textvariable=self.words_folder_var, width=35)
        self.words_folder_entry.pack(side="left", fill="x", expand=True)
        
        self.create_button(words_folder_frame, "찾기", self.select_words_folder, width=8).pack(side="right", padx=(5, 0))
        
        # 결과 폴더
        self.create_label(folder_frame, "결과 폴더:").pack(anchor="w", padx=10, pady=5)
        results_folder_frame = tk.Frame(folder_frame, bg=self.theme.get_color("bg"))
        results_folder_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.results_folder_var = tk.StringVar()
        self.results_folder_entry = self.create_entry(results_folder_frame, textvariable=self.results_folder_var, width=35)
        self.results_folder_entry.pack(side="left", fill="x", expand=True)
        
        self.create_button(results_folder_frame, "찾기", self.select_results_folder, width=8).pack(side="right", padx=(5, 0))
        
        # 버튼 프레임
        btn_frame = tk.Frame(main_frame, bg=self.theme.get_color("bg"))
        btn_frame.pack(fill="x", pady=10)
        
        self.create_button(btn_frame, "💾 저장", self.save_settings, 
                          bg=self.theme.get_color("highlight")).pack(side="left", padx=5)
        self.create_button(btn_frame, "🔄 초기화", self.reset_settings).pack(side="left", padx=5)
        self.create_button(btn_frame, "❌ 취소", self.root.destroy).pack(side="right", padx=5)
        
        # 상태 표시 라벨
        self.status_label = self.create_label(main_frame, "", 
                                            font=(self.font_family, 10),
                                            fg=self.theme.get_color("highlight"))
        self.status_label.pack(pady=(10, 0))
    
    def load_current_settings(self):
        """현재 설정을 로드합니다."""
        # 전달받은 config 객체를 그대로 사용 (새로 생성하지 않음)
        
        # API 키 로드
        current_api_key = os.getenv('OPENAI_API_KEY', '')
        if current_api_key and current_api_key != 'your_openai_api_key_here':
            self.api_key_entry.delete(0, tk.END)
            self.api_key_entry.insert(0, current_api_key)
        
        # 테마 설정 로드
        current_theme = self.config.get("ui.theme", "dark")
        logger.info(f"=== 설정 로드 디버깅 ===")
        logger.info(f"Config에서 읽은 테마: {current_theme}")
        
        # 현재 테마 변수 설정
        self.current_theme.set(current_theme)
        
        # 테마 버튼 스타일 업데이트
        self.update_theme_buttons(current_theme)
        
        logger.info(f"테마 스위치 초기화 완료: {current_theme}")
        
        # 폴더 설정 로드
        words_folder = self.config.get("paths.words_folder", "words")
        results_folder = self.config.get("paths.results_folder", "results")
        
        self.words_folder_var.set(words_folder)
        self.results_folder_var.set(results_folder)
        
        logger.info(f"설정 로드 완료 - 테마: {current_theme}, 단어폴더: {words_folder}, 결과폴더: {results_folder}")
    
    def switch_theme(self, new_theme):
        """테마를 전환합니다."""
        try:
            current_theme = self.config.get('ui.theme', 'dark')
            logger.info(f"=== 테마 스위치 디버깅 ===")
            logger.info(f"버튼 클릭으로 선택된 테마: {new_theme}")
            logger.info(f"Config에서 읽은 현재 테마: {current_theme}")
            logger.info(f"테마 변경 요청: {current_theme} → {new_theme}")
            
            if new_theme != current_theme:
                logger.info(f"테마가 다르므로 변경 진행")
                self.config.set('ui.theme', new_theme)
                logger.info(f"config.set 호출 후 테마: {self.config.get('ui.theme')}")
                
                # 현재 테마 변수 업데이트
                self.current_theme.set(new_theme)
                
                # 버튼 스타일 업데이트
                self.update_theme_buttons(new_theme)
                
                # 설정 즉시 저장
                self.config.save_config()
                logger.info(f"테마가 {new_theme}로 변경되어 저장되었습니다.")
                
                # 테마 매니저 업데이트
                self.theme.set_theme(new_theme)
                
                # 현재 설정 창 테마 적용
                self.apply_theme()
                
                # 메인 창의 테마 새로고침 요청
                if self.callback:
                    logger.info("콜백을 통해 메인 창 테마 새로고침 요청")
                    self.callback()
                    
                # 상태 표시
                self.theme_status_label.config(text=f"✓ {new_theme.title()}")
                self.root.after(2000, lambda: self.theme_status_label.config(text=""))
            else:
                logger.info(f"동일한 테마이므로 변경하지 않음")
                
        except Exception as e:
            logger.error(f"테마 스위치 중 오류: {e}")
            messagebox.showerror("오류", f"테마 변경 중 오류가 발생했습니다: {e}")
    
    def update_theme_buttons(self, selected_theme):
        """테마 버튼의 스타일을 업데이트합니다."""
        try:
            # 기본 버튼 색상
            normal_bg = self.theme.get_color("btn_bg")
            normal_fg = self.theme.get_color("btn_fg")
            
            # 활성 버튼 색상 (강조)
            active_bg = self.theme.get_color("highlight")
            active_fg = "#ffffff"
            
            if selected_theme == "dark":
                # Dark 버튼 활성화
                self.dark_btn.configure(bg=active_bg, fg=active_fg)
                self.light_btn.configure(bg=normal_bg, fg=normal_fg)
            else:
                # Light 버튼 활성화  
                self.light_btn.configure(bg=active_bg, fg=active_fg)
                self.dark_btn.configure(bg=normal_bg, fg=normal_fg)
                
        except Exception as e:
            logger.error(f"테마 버튼 업데이트 중 오류: {e}")
    
    def select_words_folder(self):
        """단어 파일 폴더를 선택합니다."""
        current_folder = self.words_folder_var.get()
        if not os.path.exists(current_folder):
            current_folder = os.path.expanduser("~")
        
        folder = filedialog.askdirectory(
            title="단어 파일 폴더 선택",
            initialdir=current_folder
        )
        if folder:
            self.words_folder_var.set(folder)
    
    def select_results_folder(self):
        """결과 폴더를 선택합니다."""
        current_folder = self.results_folder_var.get()
        if not os.path.exists(current_folder):
            current_folder = os.path.expanduser("~")
        
        folder = filedialog.askdirectory(
            title="결과 폴더 선택",
            initialdir=current_folder
        )
        if folder:
            self.results_folder_var.set(folder)
    
    def reset_settings(self):
        """설정을 초기화합니다."""
        if messagebox.askyesno("설정 초기화", "모든 설정을 초기값으로 되돌리시겠습니까?"):
            self.api_key_entry.delete(0, tk.END)
            self.current_theme.set("dark")
            self.update_theme_buttons("dark")
            self.words_folder_var.set("words")
            self.results_folder_var.set("results")
            self.show_info("초기화 완료", "설정이 초기값으로 되돌아갔습니다.")
    
    def save_settings(self):
        """설정을 저장합니다."""
        try:
            logger.info("설정 저장 시작")
            
            # API 키 저장 (.env 파일에)
            api_key = self.api_key_entry.get().strip()
            if api_key and api_key != 'your_openai_api_key_here':
                env_path = Path(".env")
                env_content = f"OPENAI_API_KEY={api_key}\n"
                with open(env_path, 'w') as f:
                    f.write(env_content)
                os.environ['OPENAI_API_KEY'] = api_key
                logger.info("API 키 저장 완료")
            
            # UI 설정 저장
            new_theme = self.current_theme.get()
            self.config.set("ui.theme", new_theme)
            logger.info(f"테마 설정 저장: {new_theme}")
            
            # 폴더 설정 저장
            words_folder = self.words_folder_var.get().strip()
            results_folder = self.results_folder_var.get().strip()
            
            if words_folder:
                self.config.set("paths.words_folder", words_folder)
                logger.info(f"단어 폴더 설정 저장: {words_folder}")
            if results_folder:
                self.config.set("paths.results_folder", results_folder)
                logger.info(f"결과 폴더 설정 저장: {results_folder}")
            
            # 폴더가 없으면 생성
            for folder in [words_folder, results_folder]:
                if folder and not os.path.exists(folder):
                    try:
                        os.makedirs(folder, exist_ok=True)
                        logger.info(f"폴더 생성됨: {folder}")
                    except Exception as e:
                        logger.warning(f"폴더 생성 실패: {folder}, 오류: {e}")
            
            # 설정 파일에 저장
            logger.info(f"저장 전 테마 설정: {self.config.get('ui.theme')}")
            self.config.save_config()
            logger.info("config.json 파일 저장 완료")
            
            # 저장 후 확인
            logger.info(f"저장 후 테마 설정: {self.config.get('ui.theme')}")
            
            # 성공 메시지 표시
            self.show_info("설정 저장", "설정이 성공적으로 저장되었습니다.\n변경된 설정이 적용됩니다.")
            
            # 콜백 호출 (메인 창에 변경사항 알림)
            if self.callback:
                logger.info("설정 변경 콜백 호출")
                self.callback()
            
            # 창 닫기
            self.root.destroy()
            
        except Exception as e:
            error_msg = f"설정 저장 중 오류가 발생했습니다: {e}"
            self.show_error("설정 저장 실패", error_msg)
            logger.error(f"설정 저장 실패: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
    
    def apply_theme(self):
        """현재 창에 테마를 적용합니다."""
        try:
            # 루트 창 배경
            self.root.configure(bg=self.theme.get_color("bg"))
            
            # 모든 Label 위젯 업데이트
            for widget in self.root.winfo_children():
                self._update_widget_theme(widget)
                
        except Exception as e:
            logging.error(f"테마 적용 중 오류: {e}")
    
    def _update_widget_theme(self, widget):
        """위젯의 테마를 재귀적으로 업데이트합니다."""
        try:
            widget_class = widget.winfo_class()
            
            if widget_class in ['Frame', 'LabelFrame', 'Label']:
                widget.configure(bg=self.theme.get_color("bg"))
                if hasattr(widget, 'configure') and 'fg' in widget.keys():
                    widget.configure(fg=self.theme.get_color("fg"))
            elif widget_class == 'Button':
                widget.configure(
                    bg=self.theme.get_color("btn_bg"),
                    fg=self.theme.get_color("btn_fg"),
                    activebackground=self.theme.get_color("btn_active_bg"),
                    activeforeground=self.theme.get_color("btn_active_fg"),
                    highlightcolor=self.theme.get_color("btn_bg"),
                    highlightbackground=self.theme.get_color("btn_bg")
                )
            
            # 자식 위젯들도 업데이트
            for child in widget.winfo_children():
                self._update_widget_theme(child)
                
        except Exception as e:
            logging.debug(f"위젯 테마 업데이트 중 오류 (무시됨): {e}")
    
    def test_api_key(self):
        """API 키를 테스트합니다."""
        try:
            api_key = self.api_key_entry.get().strip()
            if not api_key:
                self.show_warning("API 키 없음", "API 키를 입력해주세요.")
                return
            
            # 임시로 환경 변수 설정
            original_key = os.getenv('OPENAI_API_KEY')
            os.environ['OPENAI_API_KEY'] = api_key
            
            try:
                client = OpenAI(api_key=api_key)
                # 간단한 테스트 요청
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                self.show_info("API 키 테스트", "API 키가 유효합니다!")
            finally:
                # 원래 키 복원
                if original_key:
                    os.environ['OPENAI_API_KEY'] = original_key
                elif 'OPENAI_API_KEY' in os.environ:
                    del os.environ['OPENAI_API_KEY']
                    
        except Exception as e:
            self.show_error("API 키 테스트 실패", f"API 키가 유효하지 않습니다: {e}")
