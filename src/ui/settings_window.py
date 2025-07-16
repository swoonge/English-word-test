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
        super().__init__(config, "설정", "500x450")
        self.callback = callback
        self.setup_ui()
        self.load_current_settings()
    
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
        
        self.create_label(ui_frame, "테마:").pack(anchor="w", padx=10, pady=5)
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var, 
                                   values=["dark", "light"], state="readonly")
        theme_combo.pack(fill="x", padx=10, pady=(0, 10))
        
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
    
    def load_current_settings(self):
        """현재 설정을 로드합니다."""
        current_api_key = os.getenv('OPENAI_API_KEY', '')
        if current_api_key:
            self.api_key_entry.insert(0, current_api_key)
        
        self.theme_var.set(self.config.get("ui.theme", "dark"))
        self.words_folder_var.set(self.config.get("paths.words_folder", "words"))
        self.results_folder_var.set(self.config.get("paths.results_folder", "results"))
    
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
            self.theme_var.set("dark")
            self.words_folder_var.set("words")
            self.results_folder_var.set("results")
            self.show_info("초기화 완료", "설정이 초기값으로 되돌아갔습니다.")
    
    def save_settings(self):
        """설정을 저장합니다."""
        try:
            # API 키 저장 (.env 파일에)
            api_key = self.api_key_entry.get().strip()
            if api_key:
                env_path = Path(".env")
                env_content = f"OPENAI_API_KEY={api_key}\n"
                with open(env_path, 'w') as f:
                    f.write(env_content)
                os.environ['OPENAI_API_KEY'] = api_key
            
            # UI 설정 저장
            self.config.config["ui"]["theme"] = self.theme_var.get()
            
            # 폴더 설정 저장
            words_folder = self.words_folder_var.get().strip()
            results_folder = self.results_folder_var.get().strip()
            
            if words_folder:
                self.config.config["paths"]["words_folder"] = words_folder
            if results_folder:
                self.config.config["paths"]["results_folder"] = results_folder
            
            # 폴더가 없으면 생성
            for folder in [words_folder, results_folder]:
                if folder and not os.path.exists(folder):
                    try:
                        os.makedirs(folder, exist_ok=True)
                        logger.info(f"폴더 생성됨: {folder}")
                    except Exception as e:
                        logger.warning(f"폴더 생성 실패: {folder}, 오류: {e}")
            
            self.config.save_config()
            
            self.show_info("설정 저장", "설정이 성공적으로 저장되었습니다.")
            if self.callback:
                self.callback()
            self.root.destroy()
            
        except Exception as e:
            self.show_error("설정 저장 실패", f"설정 저장 중 오류가 발생했습니다: {e}")
            logger.error(f"설정 저장 실패: {e}")
    
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
