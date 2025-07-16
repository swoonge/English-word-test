
import os
import random
import datetime
import logging
import json
import platform
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from openai import OpenAI

# pyperclip 클립보드 지원 (선택적)
try:
    import pyperclip
except ImportError:
    pyperclip = None

# 환경 변수 로딩
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,  # INFO에서 DEBUG로 변경
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('word_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WordPair:
    """영어 단어와 한국어 의미를 저장하는 데이터 클래스"""
    eng: str
    kor: str
    
    def __post_init__(self):
        self.eng = self.eng.strip()
        self.kor = self.kor.strip()

@dataclass
class TestResult:
    """시험 결과를 저장하는 데이터 클래스"""
    words: List[WordPair]
    user_answers: Dict[str, str]
    gpt_result: str
    date_str: str
    score: Optional[int] = None

class Config:
    """설정 관리 클래스"""
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.default_config = {
            "ui": {
                "theme": "dark",
                "font_family": "Arial",
                "font_size": 12,
                "window_geometry": {
                    "main": "500x350",
                    "test": "600x800",
                    "result": "900x700"
                }
            },
            "openai": {
                "model": "gpt-4o",
                "temperature": 0.1,
                "max_tokens": 2000
            },
            "paths": {
                "results_folder": "results",
                "words_folder": "words"
            },
            "recent_files": []
        }
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """설정 파일을 로드합니다."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 기본 설정과 병합
                return {**self.default_config, **config}
            else:
                self.save_config(self.default_config)
                return self.default_config
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return self.default_config
    
    def save_config(self, config: dict = None):
        """설정을 파일에 저장합니다."""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            logger.info("설정이 저장되었습니다.")
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
    
    def get(self, key_path: str, default=None):
        """점 표기법으로 설정 값을 가져옵니다. 예: 'ui.theme'"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

class OpenAIService:
    """OpenAI API 서비스 클래스"""
    
    def __init__(self, config: Config):
        self.config = config
        self._client = None
    
    @property
    def client(self) -> OpenAI:
        """OpenAI 클라이언트를 지연 초기화합니다."""
        if self._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key or api_key == "YOUR_OPENAI_API_KEY":
                raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
            self._client = OpenAI(api_key=api_key)
        return self._client
    
    def grade_test(self, words: List[WordPair], user_answers: Dict[str, str]) -> str:
        """GPT를 사용하여 시험을 채점합니다."""
        # API 키 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == "YOUR_OPENAI_API_KEY":
            logger.warning("OpenAI API 키가 설정되지 않았습니다. 수동 채점용 결과를 생성합니다.")
            return self._create_manual_grading_result(words, user_answers)
        
        try:
            prompt = self._create_grading_prompt(words, user_answers)
            response = self.client.chat.completions.create(
                model=self.config.get("openai.model", "gpt-4o"),
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.get("openai.temperature", 0.1),
                max_tokens=self.config.get("openai.max_tokens", 2000)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GPT 채점 중 오류 발생: {e}")
            return self._create_fallback_result(words, user_answers, str(e))
    
    def _create_grading_prompt(self, words: List[WordPair], user_answers: Dict[str, str]) -> str:
        """채점용 프롬프트를 생성합니다."""
        table = "| 번호 | 영어 | 정답 | 내 답 |\n|---|---|---|---|\n"
        for i, word in enumerate(words, 1):
            ans = user_answers.get(word.eng, "")
            table += f"| {i} | {word.eng} | {word.kor} | {ans} |\n"
        
        return f"""아래는 영어 단어 시험 결과입니다.
토익 단어 기준으로, 정답(뜻)과 '내 답'이 의미가 거의 같거나 맞춤법이 약간 틀린 경우에도 'O'(정답)으로 처리해주세요. 
단, 의미가 확실히 다르거나 빈칸인 경우 'X'로 처리해주세요.
아래 표를 채점해서, 맨 오른쪽에 '채점' 열을 추가해서 O/X를 표로 표시해주세요.

{table}

- 설명, 해설 등은 필요 없고, 채점된 표만 깔끔하게 마크다운으로 보내주세요.
- 표 형식을 정확히 유지해주세요."""
    
    def _create_fallback_result(self, words: List[WordPair], user_answers: Dict[str, str], error_msg: str) -> str:
        """오류 시 대체 결과를 생성합니다."""
        table = "| 번호 | 영어 | 정답 | 내 답 | 채점 |\n|---|---|---|---|---|\n"
        for i, word in enumerate(words, 1):
            ans = user_answers.get(word.eng, "")
            table += f"| {i} | {word.eng} | {word.kor} | {ans} | - |\n"
        table += f"\n**오류 발생으로 인한 수동 채점 필요**\n오류 내용: {error_msg}"
        return table
    
    def _create_manual_grading_result(self, words: List[WordPair], user_answers: Dict[str, str]) -> str:
        """API 키가 없을 때 수동 채점용 결과를 생성합니다."""
        table = "| 번호 | 영어 | 정답 | 내 답 | 채점 |\n|---|---|---|---|---|\n"
        
        for i, word in enumerate(words, 1):
            ans = user_answers.get(word.eng, "").strip()
            
            # 간단한 자동 채점 (정확히 일치하는 경우만)
            if ans.lower() == word.kor.lower():
                grade = "O"
            elif not ans:  # 빈 답안
                grade = "X"
            else:
                grade = "?"  # 수동 확인 필요
            
            table += f"| {i} | {word.eng} | {word.kor} | {ans} | {grade} |\n"
        
        table += f"\n**📝 수동 채점 안내**\n"
        table += f"• O: 정답 (자동 확인됨)\n"
        table += f"• X: 오답 (빈 답안)\n" 
        table += f"• ?: 수동 확인 필요 - 정답과 비교하여 O 또는 X로 수정하세요\n\n"
        table += f"💡 **OpenAI API 키를 설정하면 자동 채점이 가능합니다**\n"
        table += f"설정 → 환경 설정에서 API 키를 입력해주세요."
        
        return table

class MarkdownParser:
    """마크다운 파일에서 단어를 추출하는 클래스"""
    
    HEADER_KEYWORDS = ['word', 'english', '영어', 'vocabulary', '단어', 'meaning', '뜻']
    
    @classmethod
    def parse_words_from_file(cls, file_path: str) -> List[WordPair]:
        """마크다운 파일에서 단어 목록을 추출합니다."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            words = cls._extract_words_from_content(content)
            logger.info(f"마크다운에서 추출된 단어 수: {len(words)}")
            if words:
                logger.info(f"첫 번째 단어 예시: {words[0]}")
            
            return words
            
        except Exception as e:
            logger.error(f"마크다운 파싱 중 오류 발생: {e}")
            return []
    
    @classmethod
    def _extract_words_from_content(cls, content: str) -> List[WordPair]:
        """마크다운 내용에서 단어를 추출합니다."""
        lines = content.split('\n')
        table_lines = cls._extract_table_lines(lines)
        
        if not table_lines:
            logger.warning("마크다운 파일에서 테이블을 찾을 수 없습니다.")
            return []
        
        words = []
        for line in table_lines:
            words.extend(cls._parse_table_row(line))
        
        return words
    
    @classmethod
    def _extract_table_lines(cls, lines: List[str]) -> List[str]:
        """테이블 라인들을 추출합니다."""
        table_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith('|') and '---' not in line:
                table_lines.append(line)
        return table_lines
    
    @classmethod
    def _parse_table_row(cls, line: str) -> List[WordPair]:
        """테이블 행을 파싱하여 단어 쌍을 추출합니다."""
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        words = []
        
        if len(cells) >= 4:
            # 4열 구조: 영어-뜻-영어-뜻
            word1 = WordPair(cells[0], cells[1])
            word2 = WordPair(cells[2], cells[3])
            
            if cls._is_valid_word(word1):
                words.append(word1)
            if cls._is_valid_word(word2):
                words.append(word2)
                
        elif len(cells) >= 2:
            # 2열 구조: 영어-뜻
            word = WordPair(cells[0], cells[1])
            if cls._is_valid_word(word):
                words.append(word)
        
        return words
    
    @classmethod
    def _is_valid_word(cls, word: WordPair) -> bool:
        """유효한 단어인지 확인합니다."""
        if not word.eng or not word.kor:
            return False
        
        # 헤더 키워드 확인
        for keyword in cls.HEADER_KEYWORDS:
            if keyword in word.eng.lower():
                return False
        
        return True

class ThemeManager:
    """테마 관리 클래스"""
    
    THEMES = {
        "dark": {
            "bg": "#23272e",
            "fg": "#f5f6fa",
            "btn_bg": "#444c56",
            "btn_fg": "#f5f6fa",
            "entry_bg": "#2d333b",
            "entry_fg": "#f5f6fa",
            "highlight": "#2986cc",
            "success": "#4caf50",
            "error": "#f44336"
        },
        "light": {
            "bg": "#ffffff",
            "fg": "#333333",
            "btn_bg": "#e0e0e0",
            "btn_fg": "#333333",
            "entry_bg": "#ffffff",
            "entry_fg": "#333333",
            "highlight": "#2986cc",
            "success": "#4caf50",
            "error": "#f44336"
        }
    }
    
    def __init__(self, theme_name: str = "dark"):
        self.current_theme = self.THEMES.get(theme_name, self.THEMES["dark"])
    
    def get_color(self, key: str) -> str:
        """테마 색상을 가져옵니다."""
        return self.current_theme.get(key, "#000000")

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
            "activebackground": self.theme.get_color("highlight"),
            "activeforeground": self.theme.get_color("btn_fg"),
            "font": (self.font_family, self.font_size),
            "relief": "flat",
            "cursor": "hand2"
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

class WordTestWindow(BaseWindow):
    """단어 시험 창 클래스"""
    
    def __init__(self, config: Config, words: List[WordPair]):
        geometry = config.get("ui.window_geometry.test", "600x800")
        super().__init__(config, "단어 시험 (토익)", geometry)
        self.words = words
        self.answers = {}
        self.submitted = False
        self.entries = []
        
        # 창을 맨 앞으로 가져오기
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()
        
        self.setup_ui()
    
    def setup_ui(self):
        """시험 UI를 구성합니다."""
        if not self.words:
            self.show_error("오류", "단어 목록이 비어있습니다.")
            return
        
        # 스크롤 가능한 프레임 생성
        canvas = tk.Canvas(self.root, bg=self.theme.get_color("bg"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme.get_color("bg"))

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # 마우스 휠 지원
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 단어 입력 필드들
        for i, word in enumerate(self.words):
            label = self.create_label(scrollable_frame, f"{i+1}. {word.eng}", 
                                    font=(self.font_family, self.font_size), anchor="w")
            label.grid(row=i, column=0, padx=10, pady=3, sticky="w")
            
            entry = self.create_entry(scrollable_frame, width=40)
            entry.grid(row=i, column=1, padx=10, pady=3)
            entry.bind('<Return>', self._on_enter)
            self.entries.append(entry)

        # 제출 버튼
        submit_frame = tk.Frame(self.root, bg=self.theme.get_color("bg"))
        self.create_button(submit_frame, "제출", self.submit_test, 
                          bg=self.theme.get_color("highlight"), fg="white",
                          font=(self.font_family, self.font_size + 2), 
                          padx=20, pady=5).pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        submit_frame.pack(side="bottom", fill="x")

        # 첫 번째 입력 필드에 포커스
        if self.entries:
            self.entries[0].focus()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_enter(self, event):
        """엔터 키 이벤트 처리"""
        self.submit_test()
    
    def _on_close(self):
        """창 닫기 이벤트 처리"""
        logger.info("창 닫기 이벤트 (_on_close)")
        self.submitted = False
        logger.info("submitted = False 설정")
        if hasattr(self, 'root') and self.root:
            self.root.quit()
            self.root.destroy()
    
    def submit_test(self):
        """시험을 제출합니다."""
        logger.info("submit_test() 호출됨")
        
        # 답안 수집
        try:
            for i, word in enumerate(self.words):
                if i < len(self.entries):
                    answer = self.entries[i].get().strip()
                    self.answers[word.eng] = answer
                    logger.debug(f"답안 수집: {word.eng} -> '{answer}'")
                else:
                    logger.warning(f"입력 필드 {i}가 없습니다")
            
            logger.info(f"총 {len(self.answers)}개의 답안 수집 완료")
            self.submitted = True
            logger.info("submitted 플래그 설정됨")
            
            # 즉시 창 닫기 (after 사용하지 않고)
            if hasattr(self, 'root') and self.root:
                logger.info("창 닫기 시작")
                self.root.quit()  # mainloop 종료
                self.root.destroy()  # 창 소멸
                logger.info("창 닫기 완료")
                
        except Exception as e:
            logger.error(f"submit_test 중 오류: {e}")
            self.submitted = False
    
    def run(self) -> Optional[Dict[str, str]]:
        """시험을 실행하고 결과를 반환합니다."""
        logger.info("WordTestWindow.run() 시작")
        logger.info(f"단어 수: {len(self.words)}")
        
        try:
            # 메인 루프 실행
            self.root.mainloop()
            logger.info("mainloop 정상 종료")
        except Exception as e:
            logger.error(f"mainloop 중 오류: {e}")
            self.submitted = False
            
        # 결과 반환 전 상태 확인
        logger.info(f"mainloop 종료 후 상태:")
        logger.info(f"  - submitted: {self.submitted}")
        logger.info(f"  - answers 존재: {self.answers is not None}")
        logger.info(f"  - answers 개수: {len(self.answers) if self.answers else 0}")
        
        # 결과 반환
        if self.submitted and self.answers:
            logger.info("✅ 답안 반환")
            # 딕셔너리 복사본 반환 (참조 문제 방지)
            result = dict(self.answers)
            logger.info(f"반환할 답안: {result}")
            return result
        else:
            logger.warning("❌ 답안 없음 또는 제출되지 않음")
            return None

class ResultWindow(BaseWindow):
    """결과 창 클래스"""
    
    def __init__(self, config: Config, test_result: TestResult):
        geometry = config.get("ui.window_geometry.result", "900x700")
        super().__init__(config, "채점 결과 확인 및 저장", geometry)
        self.test_result = test_result
        self.result_saved = False
        self.saved_path = None
        self.clipboard_available = self._check_clipboard()
        
        # 창을 맨 앞으로 가져오기
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.focus_force()
        
        self.setup_ui()
    
    def _check_clipboard(self) -> bool:
        """클립보드 모듈 가용성을 확인합니다."""
        try:
            return pyperclip is not None
        except:
            logger.warning("pyperclip이 설치되지 않아 복사 기능을 사용할 수 없습니다.")
            return False
    
    def setup_ui(self):
        """결과 UI를 구성합니다."""
        header, data = self._parse_md_table(self.test_result.gpt_result)
        
        # 표 프레임 (스크롤 포함)
        table_frame = tk.Frame(self.root, bg=self.theme.get_color("bg"))
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        canvas = tk.Canvas(table_frame, bg=self.theme.get_color("bg"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme.get_color("bg"))

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 표 헤더
        for j, col in enumerate(header):
            label = self.create_label(scrollable_frame, col, 
                                    font=(self.font_family, self.font_size + 1, "bold"),
                                    bg=self.theme.get_color("highlight"), 
                                    fg=self.theme.get_color("btn_fg"),
                                    relief="solid", borderwidth=1)
            label.grid(row=0, column=j, sticky="nsew", padx=1, pady=1)
        
        # 표 데이터
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                # 채점 결과에 따른 색상 변경
                bg_color = self.theme.get_color("bg")
                if j == len(row) - 1:  # 마지막 열(채점 결과)
                    if cell.strip() == 'O':
                        bg_color = self.theme.get_color("success")
                    elif cell.strip() == 'X':
                        bg_color = self.theme.get_color("error")
                    elif cell.strip() == '?':
                        bg_color = "#FFA500"  # 주황색 (수동 확인 필요)
                
                label = self.create_label(scrollable_frame, cell,
                                        bg=bg_color, relief="solid", borderwidth=1)
                label.grid(row=i+1, column=j, sticky="nsew", padx=1, pady=1)
        
        # 컬럼 크기 균등
        for j in range(len(header)):
            scrollable_frame.grid_columnconfigure(j, weight=1)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 점수 표시
        score_info = self._calculate_score_info(data)
        score_frame = tk.Frame(self.root, bg=self.theme.get_color("bg"))
        score_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        if score_info['manual_count'] > 0:
            score_text = f"자동 채점: {score_info['correct']}/{score_info['auto_total']} | 수동 확인 필요: {score_info['manual_count']}개"
        else:
            score_text = f"점수: {score_info['correct']}/{score_info['total']} ({score_info['percentage']:.1f}%)"
        
        self.create_label(score_frame, score_text, 
                         font=(self.font_family, self.font_size + 2, "bold")).pack()

        # 버튼 영역
        btn_frame = tk.Frame(self.root, bg=self.theme.get_color("bg"))
        btn_frame.pack(pady=10)
        
        self.create_button(btn_frame, "💾 저장", self.save_result, 
                          bg=self.theme.get_color("highlight")).pack(side="left", padx=5)
        
        self.create_button(btn_frame, "📁 다른 이름으로 저장", self.save_as_result, 
                          bg=self.theme.get_color("highlight")).pack(side="left", padx=5)
        
        copy_btn = self.create_button(btn_frame, "📋 복사", self.copy_result, 
                                     bg=self.theme.get_color("success"))
        if not self.clipboard_available:
            copy_btn.config(state="disabled")
        copy_btn.pack(side="left", padx=5)
        
        self.create_button(btn_frame, "📊 통계 보기", self.show_statistics).pack(side="left", padx=5)
        
        self.create_button(btn_frame, "❌ 닫기", self.root.destroy).pack(side="right", padx=5)
    
    def _parse_md_table(self, md_result: str) -> Tuple[List[str], List[List[str]]]:
        """마크다운 표를 파싱합니다."""
        lines = [l.strip() for l in md_result.split('\n') if l.strip()]
        table_lines = [l for l in lines if l.startswith('|')]
        rows = []
        for l in table_lines:
            cells = [c.strip() for c in l.split('|')[1:-1]]
            rows.append(cells)
        
        # 헤더, 구분선, 데이터 분리
        if len(rows) >= 2 and all('-' in c for c in rows[1]):
            header = rows[0]
            data = rows[2:]
        else:
            header = rows[0] if rows else []
            data = rows[1:] if len(rows) > 1 else []
        
        return header, data
    
    def _calculate_score(self, data: List[List[str]]) -> int:
        """점수를 계산합니다."""
        score = 0
        for row in data:
            if row and row[-1].strip() == 'O':
                score += 1
        return score
    
    def _calculate_score_info(self, data: List[List[str]]) -> Dict[str, int]:
        """상세 점수 정보를 계산합니다."""
        correct = 0
        incorrect = 0
        manual = 0
        
        for row in data:
            if row and len(row) > 0:
                grade = row[-1].strip()
                if grade == 'O':
                    correct += 1
                elif grade == 'X':
                    incorrect += 1
                elif grade == '?':
                    manual += 1
        
        total = len(data)
        auto_total = correct + incorrect
        percentage = (correct / auto_total * 100) if auto_total > 0 else 0
        
        return {
            'correct': correct,
            'incorrect': incorrect,
            'manual_count': manual,
            'total': total,
            'auto_total': auto_total,
            'percentage': percentage
        }
    
    def save_result(self):
        """결과를 저장합니다."""
        try:
            # 기본 디렉토리 설정
            default_dir = self.config.get("paths.results_folder", "results")
            if not os.path.exists(default_dir):
                default_dir = os.path.expanduser("~")
            
            # 기본 파일명 생성
            default_filename = f"{self.test_result.date_str}_result.md"
            default_path = os.path.join(default_dir, default_filename)
            
            # 파일 저장 대화상자
            filepath = filedialog.asksaveasfilename(
                title="시험 결과 저장",
                defaultextension=".md",
                filetypes=[
                    ("Markdown files", "*.md"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                initialdir=default_dir,
                initialfile=default_filename
            )
            
            if not filepath:  # 사용자가 취소한 경우
                return
            
            # 선택한 디렉토리를 설정에 저장
            selected_dir = os.path.dirname(filepath)
            self.config.config["paths"]["results_folder"] = selected_dir
            self.config.save_config()
            
            # 결과에 시험 정보 헤더 추가
            header = f"# 영어 단어 시험 결과 - {self.test_result.date_str}\n\n"
            header += f"시험 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += f"총 문제 수: {len(self.test_result.words)}문제\n"
            
            # 점수 계산 및 추가
            _, data = self._parse_md_table(self.test_result.gpt_result)
            score_info = self._calculate_score_info(data)
            
            if score_info['manual_count'] > 0:
                header += f"자동 채점: {score_info['correct']}/{score_info['auto_total']}점\n"
                header += f"수동 확인 필요: {score_info['manual_count']}개\n"
                header += f"💡 '?' 표시된 답안은 정답과 비교하여 수동으로 채점해주세요.\n\n"
            else:
                header += f"점수: {score_info['correct']}/{score_info['total']}점 ({score_info['percentage']:.1f}%)\n\n"
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header + self.test_result.gpt_result)
            
            self.result_saved = True
            self.saved_path = filepath
            self.show_info("저장 완료", f"결과가 저장되었습니다.\n파일: {filepath}")
            logger.info(f"결과가 {filepath}에 저장되었습니다.")
            
        except Exception as e:
            self.show_error("저장 실패", f"결과 저장 중 오류가 발생했습니다: {e}")
            logger.error(f"결과 저장 실패: {e}")
    
    def save_as_result(self):
        """다른 이름으로 저장합니다."""
        try:
            # 항상 사용자가 위치와 파일명을 선택하도록
            filepath = filedialog.asksaveasfilename(
                title="다른 이름으로 저장",
                defaultextension=".md",
                filetypes=[
                    ("Markdown files", "*.md"),
                    ("Text files", "*.txt"),
                    ("HTML files", "*.html"),
                    ("All files", "*.*")
                ],
                initialdir=os.path.expanduser("~"),
                initialfile=f"{self.test_result.date_str}_result_copy.md"
            )
            
            if not filepath:  # 사용자가 취소한 경우
                return
            
            # 파일 형식에 따른 내용 생성
            if filepath.lower().endswith('.html'):
                content = self._create_html_content()
            else:
                # 결과에 시험 정보 헤더 추가
                header = f"# 영어 단어 시험 결과 - {self.test_result.date_str}\n\n"
                header += f"시험 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                header += f"총 문제 수: {len(self.test_result.words)}문제\n"
                
                # 점수 계산 및 추가
                _, data = self._parse_md_table(self.test_result.gpt_result)
                score = self._calculate_score(data)
                total = len(data)
                percentage = (score / total * 100) if total > 0 else 0
                header += f"점수: {score}/{total}점 ({percentage:.1f}%)\n\n"
                content = header + self.test_result.gpt_result
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.show_info("저장 완료", f"파일이 저장되었습니다.\n파일: {filepath}")
            logger.info(f"다른 이름으로 저장됨: {filepath}")
            
        except Exception as e:
            self.show_error("저장 실패", f"파일 저장 중 오류가 발생했습니다: {e}")
            logger.error(f"다른 이름으로 저장 실패: {e}")
    
    def _create_html_content(self) -> str:
        """HTML 형식의 내용을 생성합니다."""
        header, data = self._parse_md_table(self.test_result.gpt_result)
        score_info = self._calculate_score_info(data)
        
        html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>영어 단어 시험 결과 - {self.test_result.date_str}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .correct {{ background-color: #d4edda; }}
        .incorrect {{ background-color: #f8d7da; }}
        .manual {{ background-color: #fff3cd; }}
        .header {{ margin-bottom: 20px; }}
        .legend {{ margin-top: 20px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>영어 단어 시험 결과 - {self.test_result.date_str}</h1>
        <p>시험 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"""
        
        if score_info['manual_count'] > 0:
            html += f"""        <p>자동 채점: {score_info['correct']}/{score_info['auto_total']}점</p>
        <p>수동 확인 필요: {score_info['manual_count']}개</p>"""
        else:
            html += f"""        <p>점수: {score_info['correct']}/{score_info['total']}점 ({score_info['percentage']:.1f}%)</p>"""
        
        html += """    </div>
    <table>
        <tr>
"""
        
        # 헤더 추가
        for col in header:
            html += f"            <th>{col}</th>\n"
        html += "        </tr>\n"
        
        # 데이터 추가
        for row in data:
            html += "        <tr>\n"
            for i, cell in enumerate(row):
                css_class = ""
                if i == len(row) - 1:  # 마지막 열(채점 결과)
                    if cell.strip() == 'O':
                        css_class = ' class="correct"'
                    elif cell.strip() == 'X':
                        css_class = ' class="incorrect"'
                    elif cell.strip() == '?':
                        css_class = ' class="manual"'
                html += f"            <td{css_class}>{cell}</td>\n"
            html += "        </tr>\n"
        
        html += """    </table>
    <div class="legend">
        <p><strong>범례:</strong></p>
        <p><span style="background-color: #d4edda; padding: 2px 6px;">초록</span> = 정답 (O)</p>
        <p><span style="background-color: #f8d7da; padding: 2px 6px;">빨강</span> = 오답 (X)</p>"""
        
        if score_info['manual_count'] > 0:
            html += """        <p><span style="background-color: #fff3cd; padding: 2px 6px;">노랑</span> = 수동 확인 필요 (?)</p>"""
        
        html += """    </div>
</body>
</html>"""
        return html
    
    def show_statistics(self):
        """상세 통계를 보여줍니다."""
        _, data = self._parse_md_table(self.test_result.gpt_result)
        if not data:
            self.show_warning("통계 없음", "채점 데이터가 없습니다.")
            return
        
        score_info = self._calculate_score_info(data)
        
        # 틀린 문제들 목록
        wrong_words = []
        manual_words = []
        
        for row in data:
            if row and len(row) >= 4:
                if row[-1].strip() == 'X':
                    wrong_words.append(f"• {row[1]} → {row[2]} (내 답: {row[3]})")
                elif row[-1].strip() == '?':
                    manual_words.append(f"• {row[1]} → {row[2]} (내 답: {row[3]})")
        
        stats_text = f"""📊 시험 통계

✅ 맞힌 문제: {score_info['correct']}개
❌ 틀린 문제: {score_info['incorrect']}개
❓ 수동 확인 필요: {score_info['manual_count']}개
📝 전체 문제: {score_info['total']}개
"""
        
        if score_info['auto_total'] > 0:
            stats_text += f"📈 자동 채점 정답률: {score_info['percentage']:.1f}%\n\n"
        
        if wrong_words:
            stats_text += "❌ 틀린 문제들:\n" + "\n".join(wrong_words[:5])
            if len(wrong_words) > 5:
                stats_text += f"\n... 외 {len(wrong_words) - 5}개\n\n"
        
        if manual_words:
            stats_text += "❓ 수동 확인이 필요한 문제들:\n" + "\n".join(manual_words[:5])
            if len(manual_words) > 5:
                stats_text += f"\n... 외 {len(manual_words) - 5}개\n\n"
            stats_text += "💡 이 문제들은 정답과 비교하여 직접 채점해주세요."
        
        if not wrong_words and not manual_words:
            stats_text += "🎉 자동으로 확인된 모든 문제를 맞혔습니다!"
        
        messagebox.showinfo("상세 통계", stats_text)
    
    def copy_result(self):
        """결과를 클립보드에 복사합니다."""
        if not self.clipboard_available:
            self.show_error("복사 불가", "pyperclip 모듈이 설치되지 않았습니다.\n'pip install pyperclip'을 실행한 후 다시 시도하세요.")
            return
        
        try:
            md_table = self._extract_md_table(self.test_result.gpt_result)
            pyperclip.copy(md_table)
            self.show_info("복사 완료", "결과 표가 마크다운으로 복사되었습니다!\n노션 등에 붙여넣기 하세요.")
        except Exception as e:
            self.show_error("복사 오류", f"클립보드 복사 실패: {e}")
    
    def _extract_md_table(self, md_result: str) -> str:
        """마크다운 표만 추출합니다."""
        lines = md_result.split('\n')
        table = []
        in_table = False
        for line in lines:
            if line.strip().startswith('|'):
                table.append(line)
                in_table = True
            elif in_table:
                break
        return '\n'.join(table)
    
    def run(self) -> Tuple[bool, Optional[str]]:
        """결과 창을 실행하고 저장 여부를 반환합니다."""
        self.root.mainloop()
        return self.result_saved, self.saved_path

class MainApplication(BaseWindow):
    """메인 애플리케이션 클래스"""
    
    def __init__(self):
        self.config = Config()
        geometry = self.config.get("ui.window_geometry.main", "500x350")
        
        # tkinterdnd2 사용 가능 여부 확인
        self.dnd_available = False
        try:
            from tkinterdnd2 import TkinterDnD
            self.root = TkinterDnD.Tk()
            self.dnd_available = True
            logger.info("tkinterdnd2를 사용하여 드래그 앤 드롭 기능이 활성화되었습니다.")
        except ImportError:
            self.root = tk.Tk()
            logger.warning("tkinterdnd2를 사용할 수 없어 드래그 앤 드롭 기능이 비활성화됩니다.")
        
        # 공통 초기화
        self.root.title("영어 단어 시험 - 메인")
        self.root.geometry(geometry)
        
        # 테마 초기화
        self.theme = ThemeManager(self.config.get("ui.theme", "dark"))
        self.root.configure(bg=self.theme.get_color("bg"))
        
        # 폰트 설정
        self.font_family = self.config.get("ui.font_family", "Arial")
        self.font_size = self.config.get("ui.font_size", 12)
        
        self.openai_service = OpenAIService(self.config)
        self.setup_ui()
        
        # 드래그 앤 드롭 설정 (가능한 경우만)
        if self.dnd_available:
            self._setup_drag_drop()
    
    def create_button(self, parent, text: str, command, **kwargs) -> tk.Button:
        """통일된 스타일의 버튼을 생성합니다."""
        default_style = {
            "bg": self.theme.get_color("btn_bg"),
            "fg": self.theme.get_color("btn_fg"),
            "activebackground": self.theme.get_color("highlight"),
            "activeforeground": self.theme.get_color("btn_fg"),
            "font": (self.font_family, self.font_size),
            "relief": "flat",
            "cursor": "hand2"
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
    
    def setup_ui(self):
        """메인 UI를 구성합니다."""
        # 메뉴바
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="파일 열기...", command=self.select_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        
        # 최근 파일 서브메뉴
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="최근 파일", menu=self.recent_menu)
        self._update_recent_files_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="단어 파일 폴더 열기", command=self.open_words_folder)
        file_menu.add_command(label="결과 폴더 열기", command=self.open_results_folder)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit, accelerator="Ctrl+Q")
        
        # 설정 메뉴
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="환경 설정...", command=self.open_settings, accelerator="Ctrl+,")
        settings_menu.add_separator()
        settings_menu.add_command(label="기본 폴더 재설정", command=self.reset_default_folders)
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용법", command=self.show_usage)
        help_menu.add_command(label="마크다운 형식 가이드", command=self.show_markdown_guide)
        help_menu.add_command(label="정보", command=self.show_about)
        
        # 키보드 단축키 바인딩
        self.root.bind('<Control-o>', lambda e: self.select_file())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-comma>', lambda e: self.open_settings())
        
        # 메인 콘텐츠
        main_frame = tk.Frame(self.root, bg=self.theme.get_color("bg"))
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # 제목
        title_label = self.create_label(main_frame, 
                                      "영어 단어 시험 프로그램",
                                      font=(self.font_family, 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 드래그 앤 드롭 안내
        info_label = self.create_label(main_frame,
                                     "마크다운(.md) 단어 파일을\n여기로 드래그 앤 드롭 하세요!\n\n또는 아래 버튼을 클릭하세요.",
                                     font=(self.font_family, 14))
        info_label.pack(pady=20)
        
        # 선택된 파일 표시
        self.file_label = self.create_label(main_frame, "", 
                                          font=(self.font_family, 12),
                                          fg=self.theme.get_color("highlight"))
        self.file_label.pack(pady=10)
        
        # 버튼들
        btn_frame = tk.Frame(main_frame, bg=self.theme.get_color("bg"))
        btn_frame.pack(pady=20)
        
        self.create_button(btn_frame, "📂 파일 열기", self.select_file,
                          bg=self.theme.get_color("highlight"),
                          padx=20, pady=10).pack(side="left", padx=10)
        
        self.create_button(btn_frame, "⚙️ 설정", self.open_settings,
                          padx=20, pady=10).pack(side="left", padx=10)
        
        self.create_button(btn_frame, "📁 단어 폴더", self.open_words_folder,
                          padx=20, pady=10).pack(side="left", padx=10)
    
    def _setup_drag_drop(self):
        """드래그 앤 드롭을 설정합니다."""
        try:
            from tkinterdnd2 import DND_FILES
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
            logger.info("드래그 앤 드롭 기능이 활성화되었습니다.")
        except ImportError:
            logger.warning("tkinterdnd2를 찾을 수 없어 드래그 앤 드롭 기능을 사용할 수 없습니다.")
        except Exception as e:
            logger.error(f"드래그 앤 드롭 설정 실패: {e}")
    
    def _on_drop(self, event):
        """파일 드롭 이벤트 처리"""
        file_path = event.data.strip()
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        file_path = file_path.replace('file://', '')
        file_path = file_path.strip()
        
        if not file_path.lower().endswith(('.md', '.txt')):
            self.show_error("파일 형식 오류", "마크다운(.md) 또는 텍스트(.txt) 파일만 지원합니다.")
            return
        
        if not os.path.exists(file_path):
            self.show_error("파일 없음", f"파일을 찾을 수 없습니다: {file_path}")
            return
        
        self.file_label.config(text=f"선택된 파일: {os.path.basename(file_path)}")
        logger.info(f"드래그앤드롭으로 파일 선택됨: {file_path}")
        
        # 최근 파일에 추가
        self._add_to_recent_files(file_path)
        
        self.root.after(500, lambda: self.start_test_flow(file_path))
    
    def select_file(self):
        """파일 선택 대화상자를 엽니다."""
        # 기본 디렉토리 설정 (없으면 홈 디렉토리)
        initial_dir = self.config.get("paths.words_folder", "words")
        if not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")
        
        file_path = filedialog.askopenfilename(
            title="영어 단어 마크다운 파일 선택",
            filetypes=[
                ("Markdown files", "*.md"), 
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            initialdir=initial_dir
        )
        
        if file_path:
            # 선택한 파일의 디렉토리를 설정에 저장
            selected_dir = os.path.dirname(file_path)
            self.config.config["paths"]["words_folder"] = selected_dir
            self.config.save_config()
            
            # 최근 파일에 추가
            self._add_to_recent_files(file_path)
            
            self.file_label.config(text=f"선택된 파일: {os.path.basename(file_path)}")
            logger.info(f"파일 선택됨: {file_path}")
            self.start_test_flow(file_path)
    
    def start_test_flow(self, file_path: str):
        """시험 프로세스를 시작합니다."""
        logger.info(f"start_test_flow 시작: {file_path}")
        self.root.withdraw()
        try:
            # 1. 단어 추출
            logger.info("1. 단어 추출 시작")
            words = MarkdownParser.parse_words_from_file(file_path)
            if not words:
                logger.error("단어 추출 실패")
                self.show_error("오류", "단어를 추출할 수 없습니다.")
                self.root.deiconify()
                return
            logger.info(f"단어 추출 완료: {len(words)}개")
            
            # 2. 단어 섞기
            logger.info("2. 단어 섞기")
            random.shuffle(words)
            
            # 3. 시험 실행
            logger.info("3. 시험 창 생성 및 실행")
            test_window = WordTestWindow(self.config, words)
            logger.info("시험 창 생성 완료")
            
            # 시험 시작 알림 (선택적)
            # self.show_info("시험 시작", f"{len(words)}개의 단어 시험을 시작합니다.")
            
            user_answers = test_window.run()
            logger.info(f"시험 창 실행 완료. 답안: {user_answers is not None}")
            
            if user_answers is None:
                logger.warning("사용자가 시험을 취소하거나 답안이 없음")
                self.show_info("알림", "시험이 취소되었습니다.")
                self.root.deiconify()
                return
            
            logger.info(f"답안 개수: {len(user_answers)}")
            
            # 채점 진행 알림
            self.show_info("채점 중", "답안을 채점하고 있습니다. 잠시만 기다려주세요...")
            
            # 4. GPT 채점
            logger.info("4. GPT 채점 시작")
            gpt_result = self.openai_service.grade_test(words, user_answers)
            logger.info("GPT 채점 완료")
            
            # 5. 결과 표시
            logger.info("5. 결과 창 생성")
            date_str = os.path.splitext(os.path.basename(file_path))[0]
            test_result = TestResult(words, user_answers, gpt_result, date_str)
            
            result_window = ResultWindow(self.config, test_result)
            logger.info("결과 창 생성 완료")
            result_window.run()
            logger.info("결과 창 실행 완료")
            
            self.root.deiconify()
            logger.info("메인 창 다시 표시")
            
        except Exception as e:
            error_msg = f"프로그램 실행 중 오류가 발생했습니다:\n{e}"
            logger.error(error_msg)
            logger.error(f"상세 오류: {e.__class__.__name__}: {str(e)}")
            import traceback
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            self.show_error("오류", error_msg)
            self.root.deiconify()
    
    def open_settings(self):
        """설정 창을 엽니다."""
        settings_window = SettingsWindow(self.config, self._on_settings_changed)
    
    def _on_settings_changed(self):
        """설정 변경 시 호출됩니다."""
        # 설정이 변경되면 UI를 새로고침할 수 있습니다
        logger.info("설정이 변경되었습니다.")
    
    def _update_recent_files_menu(self):
        """최근 파일 메뉴를 업데이트합니다."""
        self.recent_menu.delete(0, tk.END)
        
        recent_files = self.config.get("recent_files", [])
        if not recent_files:
            self.recent_menu.add_command(label="최근 파일 없음", state="disabled")
        else:
            for file_path in recent_files[-10:]:  # 최대 10개
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    self.recent_menu.add_command(
                        label=filename,
                        command=lambda f=file_path: self._open_recent_file(f)
                    )
            self.recent_menu.add_separator()
            self.recent_menu.add_command(label="최근 파일 목록 지우기", command=self._clear_recent_files)
    
    def _open_recent_file(self, file_path: str):
        """최근 파일을 엽니다."""
        if os.path.exists(file_path):
            self.file_label.config(text=f"선택된 파일: {os.path.basename(file_path)}")
            self.start_test_flow(file_path)
        else:
            self.show_error("파일 없음", f"파일을 찾을 수 없습니다: {file_path}")
            self._remove_from_recent_files(file_path)
    
    def _clear_recent_files(self):
        """최근 파일 목록을 지웁니다."""
        self.config.config["recent_files"] = []
        self.config.save_config()
        self._update_recent_files_menu()
        self.show_info("목록 지우기", "최근 파일 목록이 지워졌습니다.")
    
    def _add_to_recent_files(self, file_path: str):
        """파일을 최근 파일 목록에 추가합니다."""
        recent_files = self.config.get("recent_files", [])
        
        # 기존에 있으면 제거 (중복 방지)
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # 맨 앞에 추가
        recent_files.insert(0, file_path)
        
        # 최대 10개까지만 유지
        recent_files = recent_files[:10]
        
        self.config.config["recent_files"] = recent_files
        self.config.save_config()
        self._update_recent_files_menu()
    
    def _remove_from_recent_files(self, file_path: str):
        """파일을 최근 파일 목록에서 제거합니다."""
        recent_files = self.config.get("recent_files", [])
        if file_path in recent_files:
            recent_files.remove(file_path)
            self.config.config["recent_files"] = recent_files
            self.config.save_config()
            self._update_recent_files_menu()
    
    def open_words_folder(self):
        """단어 파일 폴더를 엽니다."""
        folder_path = self.config.get("paths.words_folder", "words")
        if not os.path.exists(folder_path):
            # 폴더가 없으면 선택하도록 안내
            if messagebox.askyesno("폴더 없음", f"'{folder_path}' 폴더가 없습니다.\n새 폴더를 선택하시겠습니까?"):
                folder_path = filedialog.askdirectory(title="단어 파일 폴더 선택")
                if folder_path:
                    self.config.config["paths"]["words_folder"] = folder_path
                    self.config.save_config()
                else:
                    return
            else:
                return
        
        # 폴더 열기 (플랫폼별 명령어)
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            elif system == "Windows":
                subprocess.run(["explorer", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            self.show_error("폴더 열기 실패", f"폴더를 열 수 없습니다: {e}")
    
    def open_results_folder(self):
        """결과 폴더를 엽니다."""
        folder_path = self.config.get("paths.results_folder", "results")
        if not os.path.exists(folder_path):
            if messagebox.askyesno("폴더 없음", f"'{folder_path}' 폴더가 없습니다.\n새 폴더를 선택하시겠습니까?"):
                folder_path = filedialog.askdirectory(title="결과 폴더 선택")
                if folder_path:
                    self.config.config["paths"]["results_folder"] = folder_path
                    self.config.save_config()
                else:
                    return
            else:
                return
        
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            elif system == "Windows":
                subprocess.run(["explorer", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            self.show_error("폴더 열기 실패", f"폴더를 열 수 없습니다: {e}")
    
    def reset_default_folders(self):
        """기본 폴더를 재설정합니다."""
        if messagebox.askyesno("폴더 재설정", "기본 폴더 설정을 초기화하시겠습니까?"):
            self.config.config["paths"]["words_folder"] = "words"
            self.config.config["paths"]["results_folder"] = "results"
            self.config.save_config()
            self.show_info("재설정 완료", "기본 폴더가 'words'와 'results'로 재설정되었습니다.")
    
    def show_markdown_guide(self):
        """마크다운 형식 가이드를 표시합니다."""
        guide_text = """마크다운 단어 파일 형식 가이드

📋 기본 2열 형식:
| 영어 | 한국어 |
|------|--------|
| apple | 사과 |
| book | 책 |
| computer | 컴퓨터 |

📋 고밀도 4열 형식:
| 영어1 | 한국어1 | 영어2 | 한국어2 |
|-------|--------|-------|--------|
| apple | 사과 | book | 책 |
| cat | 고양이 | dog | 개 |

⚠️ 주의사항:
• 첫 번째 행은 헤더로 인식됩니다
• 구분선(---|---|---)은 자동으로 무시됩니다
• 빈 셀이 있는 단어는 제외됩니다
• 파일 확장자는 .md 또는 .txt를 사용하세요

💡 팁:
• 노션, 옵시디언 등에서 작성한 테이블도 사용 가능
• 복사-붙여넣기로 쉽게 만들 수 있습니다"""
        
        messagebox.showinfo("마크다운 형식 가이드", guide_text)
    
    def show_usage(self):
        """사용법을 표시합니다."""
        usage_text = """영어 단어 시험 프로그램 사용법

1. 마크다운 파일 준비:
   - 영어 단어와 한국어 의미가 표 형식으로 작성된 .md 파일

2. 파일 선택:
   - 드래그 앤 드롭 또는 "파일 선택" 버튼 사용

3. 시험 진행:
   - 영어 단어를 보고 한국어 의미 입력
   - Enter 키 또는 "제출" 버튼으로 제출

4. 결과 확인:
   - GPT 자동 채점 결과 확인
   - 결과 저장 및 복사 가능

마크다운 파일 형식:
| 영어 | 한국어 |
|------|--------|
| apple | 사과 |
| book | 책 |"""
        
        messagebox.showinfo("사용법", usage_text)
    
    def show_about(self):
        """프로그램 정보를 표시합니다."""
        about_text = """영어 단어 시험 프로그램 v2.0

개발자: AI Assistant
기능: 마크다운 기반 영어 단어 시험 및 GPT 자동 채점

주요 기능:
- 마크다운 파일 자동 파싱
- 드래그 앤 드롭 지원
- GPT 기반 자동 채점
- 다크/라이트 테마 지원
- 결과 저장 및 공유"""
        
        messagebox.showinfo("프로그램 정보", about_text)
    
    def run(self):
        """애플리케이션을 실행합니다."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("프로그램이 사용자에 의해 종료되었습니다.")
        except Exception as e:
            logger.error(f"프로그램 실행 중 오류: {e}")
            self.show_error("치명적 오류", f"프로그램 실행 중 치명적 오류가 발생했습니다:\n{e}")

def main():
    """메인 함수"""
    try:
        app = MainApplication()
        app.run()
    except Exception as e:
        logger.error(f"애플리케이션 시작 실패: {e}")
        print(f"애플리케이션 시작 실패: {e}")

if __name__ == "__main__":
    main()