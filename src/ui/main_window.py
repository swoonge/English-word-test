"""
메인 애플리케이션 창 UI
"""
import os
import random
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import logging

from .base_window import BaseWindow
from .settings_window import SettingsWindow
from .test_window import WordTestWindow
from .result_window import ResultWindow
from ..core.config import Config
from ..core.models import TestResult
from ..services.openai_service import OpenAIService
from ..utils.markdown_parser import MarkdownParser

logger = logging.getLogger(__name__)


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
        from ..utils.theme_manager import ThemeManager
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
                self._restore_main_window()
                return

            logger.info(f"단어 추출 완료: {len(words)}개")
            
            # 2. 단어 섞기
            logger.info("2. 단어 섞기")
            random.shuffle(words)
            
            # 3. 시험 실행
            logger.info("3. 시험 창 생성 및 실행")
            test_window = WordTestWindow(self.config, words)
            logger.info("시험 창 생성 완료")
            
            user_answers = test_window.run()
            logger.info(f"시험 창 실행 완료. 답안: {user_answers is not None}")
            
            if user_answers is None:
                logger.info("시험이 취소되거나 답안이 없습니다.")
                self._restore_main_window()
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
            
            # 결과 창 실행
            saved, saved_path = result_window.run()
            logger.info("결과 창 실행 완료")
            
            # 메인 창 복원 및 포커스
            self._restore_main_window()
            
            # 결과 저장 여부에 따른 안내 메시지
            if saved and saved_path:
                self.show_info("시험 완료", f"시험이 완료되었습니다!\n결과가 저장되었습니다: {os.path.basename(saved_path)}")
            else:
                self.show_info("시험 완료", "시험이 완료되었습니다!")
            
            # 파일 선택 라벨 초기화
            self.file_label.config(text="")
            
        except Exception as e:
            import traceback
            error_msg = f"프로그램 실행 중 오류가 발생했습니다:\n{e}"
            logger.error(error_msg)
            logger.error(f"상세 오류: {e.__class__.__name__}: {str(e)}")
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            self.show_error("오류", error_msg)
            self._restore_main_window()
    
    def _restore_main_window(self):
        """메인 창을 복원하고 포커스를 설정합니다."""
        logger.info("메인 창 복원 시작")
        try:
            # 창을 화면에 표시
            self.root.deiconify()
            
            # 창을 맨 앞으로 가져오기
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            
            # 포커스 설정
            self.root.focus_force()
            
            logger.info("메인 창 복원 완료")
        except Exception as e:
            logger.error(f"메인 창 복원 중 오류: {e}")
    
    def open_settings(self):
        """설정 창을 엽니다."""
        settings_window = SettingsWindow(self.config, self._on_settings_changed)
    
    def _on_settings_changed(self):
        """설정 변경 시 호출됩니다."""
        logger.info("설정이 변경되었습니다. 테마를 새로고침합니다.")
        self._refresh_theme()
    
    def _refresh_theme(self):
        """테마를 새로고침합니다."""
        # 설정 다시 로드
        self.config = Config()
        
        # 테마 매니저 업데이트
        from ..utils.theme_manager import ThemeManager
        self.theme = ThemeManager(self.config.get("ui.theme", "dark"))
        
        # 메인 창 배경색 변경
        self.root.configure(bg=self.theme.get_color("bg"))
        
        # 모든 위젯 다시 그리기 (간단한 방법: 창 새로고침)
        self.show_info("테마 변경", "테마가 변경되었습니다.\n다음 실행 시 완전히 적용됩니다.")
        logger.info("테마 새로고침 완료")
    
    def _update_recent_files_menu(self):
        """최근 파일 메뉴를 업데이트합니다."""
        self.recent_menu.delete(0, tk.END)
        
        recent_files = self.config.get("recent_files", [])
        if not recent_files:
            self.recent_menu.add_command(label="최근 파일 없음", state="disabled")
        else:
            for file_path in recent_files[:10]:  # 최대 10개만 표시
                filename = os.path.basename(file_path)
                self.recent_menu.add_command(
                    label=filename,
                    command=lambda fp=file_path: self._open_recent_file(fp)
                )
            
            self.recent_menu.add_separator()
            self.recent_menu.add_command(label="목록 지우기", command=self._clear_recent_files)
    
    def _open_recent_file(self, file_path: str):
        """최근 파일을 엽니다."""
        if os.path.exists(file_path):
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
        self.config.config["recent_files"] = recent_files[:10]
        self.config.save_config()
        self._update_recent_files_menu()
    
    def _remove_from_recent_files(self, file_path: str):
        """최근 파일 목록에서 파일을 제거합니다."""
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
            try:
                os.makedirs(folder_path, exist_ok=True)
                logger.info(f"단어 폴더 생성됨: {folder_path}")
            except Exception as e:
                logger.error(f"단어 폴더 생성 실패: {e}")
                self.show_error("폴더 열기 실패", f"폴더를 생성할 수 없습니다: {folder_path}")
                return
        
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            logger.error(f"폴더 열기 실패: {e}")
            self.show_error("폴더 열기 실패", f"폴더를 열 수 없습니다: {folder_path}")
    
    def open_results_folder(self):
        """결과 폴더를 엽니다."""
        folder_path = self.config.get("paths.results_folder", "results")
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path, exist_ok=True)
                logger.info(f"결과 폴더 생성됨: {folder_path}")
            except Exception as e:
                logger.error(f"결과 폴더 생성 실패: {e}")
                self.show_error("폴더 열기 실패", f"폴더를 생성할 수 없습니다: {folder_path}")
                return
        
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            elif platform.system() == "Windows":
                subprocess.run(["explorer", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            logger.error(f"폴더 열기 실패: {e}")
            self.show_error("폴더 열기 실패", f"폴더를 열 수 없습니다: {folder_path}")
    
    def reset_default_folders(self):
        """기본 폴더를 재설정합니다."""
        try:
            words_folder = "words"
            results_folder = "results"
            
            for folder in [words_folder, results_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder, exist_ok=True)
                    logger.info(f"기본 폴더 생성됨: {folder}")
            
            self.config.config["paths"]["words_folder"] = words_folder
            self.config.config["paths"]["results_folder"] = results_folder
            self.config.save_config()
            
            self.show_info("폴더 재설정", "기본 폴더가 재설정되었습니다.\n• words/ (단어 파일)\n• results/ (결과 파일)")
            
        except Exception as e:
            logger.error(f"폴더 재설정 실패: {e}")
            self.show_error("폴더 재설정 실패", f"기본 폴더를 만들 수 없습니다: {e}")
    
    def show_usage(self):
        """사용법을 보여줍니다."""
        usage_text = """📚 영어 단어 시험 프로그램 사용법

1️⃣ 단어 파일 준비
   • 마크다운(.md) 또는 텍스트(.txt) 파일
   • 표 형식으로 영어-한국어 단어 쌍 작성

2️⃣ 파일 열기
   • 드래그 앤 드롭으로 파일을 프로그램에 끌어다 놓기
   • 또는 "파일 열기" 버튼 클릭

3️⃣ 시험 응시
   • 영어 단어에 해당하는 한국어 뜻 입력
   • 완료 후 "제출" 버튼 클릭

4️⃣ 결과 확인
   • GPT가 자동으로 채점
   • 점수와 틀린 문제 확인
   • 결과를 파일로 저장 가능

💡 팁: 설정에서 API 키와 테마를 변경할 수 있습니다."""
        
        messagebox.showinfo("사용법", usage_text)
    
    def show_markdown_guide(self):
        """마크다운 형식 가이드를 보여줍니다."""
        guide_text = """📝 마크다운 단어 파일 형식 가이드

✅ 지원하는 형식:

1️⃣ 2열 테이블 (영어 - 한국어)
| 영어 | 한국어 |
|------|--------|
| apple | 사과 |
| book | 책 |

2️⃣ 4열 테이블 (영어-한국어-영어-한국어)
| 영어1 | 한국어1 | 영어2 | 한국어2 |
|-------|-------|-------|-------|
| apple | 사과 | book | 책 |
| cat | 고양이 | dog | 개 |

📋 작성 규칙:
• 첫 번째 행은 헤더로 인식 (word, english, 영어 등)
• 구분선(---)은 자동으로 무시됨
• 빈 칸이 있는 행은 제외됨
• 파일 확장자: .md 또는 .txt

💡 예시 파일은 words/ 폴더에서 확인하세요!"""
        
        messagebox.showinfo("마크다운 형식 가이드", guide_text)
    
    def show_about(self):
        """프로그램 정보를 보여줍니다."""
        about_text = """🚀 영어 단어 시험 프로그램 v2.0

📊 주요 기능:
• 마크다운 파일에서 단어 자동 추출
• GPT 기반 지능형 채점
• 다양한 결과 저장 형식 (MD, TXT, HTML)
• 드래그 앤 드롭 지원
• 다크/라이트 테마
• 최근 파일 기록

💻 기술 스택:
• Python 3.7+
• Tkinter (GUI)
• OpenAI GPT (채점)
• 모듈화된 아키텍처

👨‍💻 개발: AI Assistant
📅 버전: 2.0 (2024)
📄 라이선스: MIT

GitHub: github.com/your-repo"""
        
        messagebox.showinfo("프로그램 정보", about_text)
    
    def run(self):
        """애플리케이션을 실행합니다."""
        logger.info("메인 애플리케이션 시작")
        self.root.mainloop()
