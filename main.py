#!/usr/bin/env python3
"""
영어 단어 시험 프로그램 - 단순화 버전
드래그 앤 드롭으로 마크다운 파일을 가져와서 시험을 진행합니다.
"""
import os
import random
import datetime
import logging
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from openai import OpenAI

# 환경 변수 로딩
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
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
            logger.info(f"파일에서 추출된 단어 수: {len(words)}")
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

class OpenAIService:
    """OpenAI API 서비스 클래스"""
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self) -> OpenAI:
        """OpenAI 클라이언트를 지연 초기화합니다."""
        if self._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API 키가 설정되지 않았습니다.")
            self._client = OpenAI(api_key=api_key)
        return self._client
    
    def grade_test(self, words: List[WordPair], user_answers: Dict[str, str]) -> str:
        """GPT를 사용하여 시험을 채점합니다."""
        # API 키 확인
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OpenAI API 키가 설정되지 않았습니다. 수동 채점용 결과를 생성합니다.")
            return self._create_manual_grading_result(words, user_answers)
        
        try:
            prompt = self._create_grading_prompt(words, user_answers)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
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
정답과 '내 답'이 의미가 거의 같거나 맞춤법이 약간 틀린 경우에도 'O'(정답)으로 처리해주세요. 
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
            elif not ans:
                grade = "X"
            else:
                grade = "?"  # 수동 확인 필요
            
            table += f"| {i} | {word.eng} | {word.kor} | {ans} | {grade} |\n"
        
        table += f"\n**📝 수동 채점 안내**\n"
        table += f"• O: 정답 (자동 확인됨)\n"
        table += f"• X: 오답 (빈 답안)\n" 
        table += f"• ?: 수동 확인 필요 - 정답과 비교하여 O 또는 X로 수정하세요\n\n"
        table += f"💡 **OpenAI API 키를 .env 파일에 설정하면 자동 채점이 가능합니다**"
        
        return table

class WordTestWindow:
    """단어 시험 창 클래스"""
    
    def __init__(self, words: List[WordPair]):
        self.words = words
        self.answers = {}
        self.submitted = False
        self.entries = []
        
        # 창 생성
        self.root = tk.Toplevel()
        self.root.title(f"영어 단어 시험 ({len(words)}문제)")
        self.root.geometry("600x700")
        self.root.configure(bg="#ffffff")
        
        # 창을 맨 앞으로
        self.root.lift()
        self.root.focus_force()
        
        self.setup_ui()
    
    def setup_ui(self):
        """시험 UI를 구성합니다."""
        if not self.words:
            messagebox.showerror("오류", "단어 목록이 비어있습니다.")
            return
        
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 제목
        title_label = tk.Label(main_frame, text=f"영어 단어 시험 ({len(self.words)}문제)", 
                              font=("Arial", 16, "bold"), bg="#ffffff", fg="#333333")
        title_label.pack(pady=(0, 20))
        
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(main_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 마우스 휠 지원
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        canvas.focus_set()  # 포커스를 받을 수 있도록 설정
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 단어 입력 필드들
        for i, word in enumerate(self.words):
            # 문제 번호와 영어 단어
            label = tk.Label(scrollable_frame, text=f"{i+1}. {word.eng}", 
                           font=("Arial", 12), bg="#ffffff", fg="#333333", anchor="w")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            
            # 답안 입력 필드
            entry = tk.Entry(scrollable_frame, font=("Arial", 12), width=30,
                           relief="solid", borderwidth=1, bg="#ffffff", fg="#333333")
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            entry.bind('<Return>', self._on_enter)
            self.entries.append(entry)
        
        # 컬럼 설정
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 제출 버튼
        submit_frame = tk.Frame(self.root, bg="#ffffff")
        submit_frame.pack(side="bottom", fill="x", pady=10)
        
        submit_btn = tk.Button(submit_frame, text="제출", command=self.submit_test,
                              font=("Arial", 14, "bold"), bg="#007acc", fg="white",
                              relief="flat", padx=30, pady=10, cursor="hand2")
        submit_btn.pack()
        
        # 첫 번째 입력 필드에 포커스
        if self.entries:
            self.entries[0].focus()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _on_enter(self, event):
        """엔터 키 이벤트 처리"""
        current_entry = event.widget
        try:
            current_index = self.entries.index(current_entry)
            if current_index < len(self.entries) - 1:
                # 다음 입력 필드로 포커스 이동
                self.entries[current_index + 1].focus()
            else:
                # 마지막 필드면 제출
                self.submit_test()
        except ValueError:
            pass
    
    def _on_close(self):
        """창 닫기 이벤트 처리"""
        self.submitted = False
        try:
            # 이벤트 바인딩 해제
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")
        except:
            pass  # 이미 해제되었거나 오류가 발생해도 무시
        self.root.quit()
        self.root.destroy()
    
    def submit_test(self):
        """시험을 제출합니다."""
        try:
            # 답안 수집
            for i, word in enumerate(self.words):
                if i < len(self.entries):
                    answer = self.entries[i].get().strip()
                    self.answers[word.eng] = answer
            
            logger.info(f"총 {len(self.answers)}개의 답안 수집 완료")
            self.submitted = True
            
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"submit_test 중 오류: {e}")
            self.submitted = False
    
    def run(self) -> Optional[Dict[str, str]]:
        """시험을 실행하고 결과를 반환합니다."""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"시험 실행 중 오류: {e}")
            self.submitted = False
        
        if self.submitted and self.answers:
            return dict(self.answers)
        else:
            return None

class ResultWindow:
    """결과 창 클래스"""
    
    def __init__(self, test_result: TestResult):
        self.test_result = test_result
        
        # 창 생성
        self.root = tk.Toplevel()
        self.root.title("시험 결과")
        self.root.geometry("900x600")
        self.root.configure(bg="#ffffff")
        
        # 창을 맨 앞으로
        self.root.lift()
        self.root.focus_force()
        
        # 창 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.setup_ui()
    
    def setup_ui(self):
        """결과 UI를 구성합니다."""
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 제목
        title_label = tk.Label(main_frame, text="📊 시험 결과", 
                              font=("Arial", 18, "bold"), bg="#ffffff", fg="#333333")
        title_label.pack(pady=(0, 20))
        
        # 결과 표시
        self._display_results(main_frame)
        
        # 버튼 프레임
        btn_frame = tk.Frame(main_frame, bg="#ffffff")
        btn_frame.pack(pady=20)
        
        # 저장 버튼
        save_btn = tk.Button(btn_frame, text="💾 결과 저장", command=self.save_result,
                            font=("Arial", 12), bg="#28a745", fg="white",
                            relief="flat", padx=20, pady=8, cursor="hand2")
        save_btn.pack(side="left", padx=10)
        
        # 복사 버튼
        copy_btn = tk.Button(btn_frame, text="📋 결과 복사", command=self.copy_result,
                            font=("Arial", 12), bg="#17a2b8", fg="white",
                            relief="flat", padx=20, pady=8, cursor="hand2")
        copy_btn.pack(side="left", padx=10)
        
        # 닫기 버튼
        close_btn = tk.Button(btn_frame, text="❌ 닫기", command=self._on_close,
                             font=("Arial", 12), bg="#dc3545", fg="white",
                             relief="flat", padx=20, pady=8, cursor="hand2")
        close_btn.pack(side="left", padx=10)
    
    def _display_results(self, parent):
        """결과를 표시합니다."""
        header, data = self._parse_md_table(self.test_result.gpt_result)
        
        # 점수 요약
        score_info = self._calculate_score_info(data)
        score_frame = tk.Frame(parent, bg="#f8f9fa", relief="solid", borderwidth=1)
        score_frame.pack(fill="x", pady=(0, 20))
        
        if score_info['manual_count'] > 0:
            score_text = f"자동 채점: {score_info['correct']}/{score_info['auto_total']} | 수동 확인 필요: {score_info['manual_count']}개"
        else:
            score_text = f"점수: {score_info['correct']}/{score_info['total']} ({score_info['percentage']:.1f}%)"
        
        score_label = tk.Label(score_frame, text=score_text, 
                              font=("Arial", 14, "bold"), bg="#f8f9fa", fg="#333333")
        score_label.pack(pady=15)
        
        # 결과 테이블
        table_frame = tk.Frame(parent, bg="#ffffff")
        table_frame.pack(fill="both", expand=True)
        
        # 스크롤 가능한 테이블
        canvas = tk.Canvas(table_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        canvas.focus_set()  # 포커스를 받을 수 있도록 설정
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 테이블 헤더
        for j, col in enumerate(header):
            label = tk.Label(scrollable_frame, text=col, 
                           font=("Arial", 11, "bold"), bg="#e9ecef", fg="#333333",
                           relief="solid", borderwidth=1, anchor="center")
            label.grid(row=0, column=j, sticky="nsew", padx=1, pady=1)
        
        # 테이블 데이터
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                # 채점 결과에 따른 색상 변경
                bg_color = "#ffffff"
                if j == len(row) - 1:  # 마지막 열(채점 결과)
                    if cell.strip() == 'O':
                        bg_color = "#d4edda"  # 초록색
                    elif cell.strip() == 'X':
                        bg_color = "#f8d7da"  # 빨간색
                    elif cell.strip() == '?':
                        bg_color = "#fff3cd"  # 노란색
                
                label = tk.Label(scrollable_frame, text=cell, font=("Arial", 10),
                               bg=bg_color, fg="#333333", relief="solid", borderwidth=1,
                               anchor="center")
                label.grid(row=i+1, column=j, sticky="nsew", padx=1, pady=1)
        
        # 컬럼 크기 설정
        for j in range(len(header)):
            scrollable_frame.grid_columnconfigure(j, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _parse_md_table(self, md_result: str):
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
    
    def _calculate_score_info(self, data):
        """점수 정보를 계산합니다."""
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
            from tkinter import filedialog
            
            # 기본 파일명 생성
            now = datetime.datetime.now()
            default_filename = f"result_{now.strftime('%y%m%d_%H%M')}.md"
            
            # 파일 저장 대화상자
            filepath = filedialog.asksaveasfilename(
                title="시험 결과 저장",
                defaultextension=".md",
                filetypes=[
                    ("Markdown files", "*.md"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                initialfile=default_filename
            )
            
            if not filepath:
                return
            
            # 결과에 헤더 추가
            header = f"# 영어 단어 시험 결과\n\n"
            header += f"시험 일시: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += f"총 문제 수: {len(self.test_result.words)}문제\n\n"
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header + self.test_result.gpt_result)
            
            messagebox.showinfo("저장 완료", f"결과가 저장되었습니다:\n{filepath}")
            logger.info(f"결과가 {filepath}에 저장되었습니다.")
            
        except Exception as e:
            messagebox.showerror("저장 실패", f"결과 저장 중 오류가 발생했습니다: {e}")
            logger.error(f"결과 저장 실패: {e}")
    
    def copy_result(self):
        """결과를 클립보드에 복사합니다."""
        try:
            # 헤더 생성
            now = datetime.datetime.now()
            header = f"# 영어 단어 시험 결과\n\n"
            header += f"시험 일시: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += f"총 문제 수: {len(self.test_result.words)}문제\n\n"
            
            # 전체 결과 텍스트
            full_result = header + self.test_result.gpt_result
            
            # 클립보드에 복사
            self.root.clipboard_clear()
            self.root.clipboard_append(full_result)
            self.root.update()  # 클립보드 업데이트 보장
            
            messagebox.showinfo("복사 완료", "결과가 클립보드에 복사되었습니다!")
            logger.info("결과가 클립보드에 복사되었습니다.")
            
        except Exception as e:
            messagebox.showerror("복사 실패", f"결과 복사 중 오류가 발생했습니다: {e}")
            logger.error(f"결과 복사 실패: {e}")
    
    def _on_close(self):
        """창 닫기 이벤트 처리"""
        try:
            # 이벤트 바인딩 해제
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")
        except:
            pass  # 이미 해제되었거나 오류가 발생해도 무시
        
        # 창 닫기
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """결과 창을 실행합니다."""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"결과 창 실행 중 오류: {e}")
            self._on_close()

class MainApplication:
    """메인 애플리케이션 클래스"""
    
    def __init__(self):
        # tkinterdnd2 사용 가능 여부 확인
        self.dnd_available = False
        try:
            from tkinterdnd2 import TkinterDnD
            self.root = TkinterDnD.Tk()
            self.dnd_available = True
            logger.info("드래그 앤 드롭 기능이 활성화되었습니다.")
        except ImportError:
            self.root = tk.Tk()
            logger.warning("tkinterdnd2를 사용할 수 없어 드래그 앤 드롭 기능이 비활성화됩니다.")
        
        # 기본 설정
        self.root.title("영어 단어 시험 프로그램")
        self.root.geometry("500x300")
        self.root.configure(bg="#ffffff")
        
        self.openai_service = OpenAIService()
        self.setup_ui()
        
        # 드래그 앤 드롭 설정
        if self.dnd_available:
            self._setup_drag_drop()
    
    def setup_ui(self):
        """메인 UI를 구성합니다."""
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # 제목
        title_label = tk.Label(main_frame, text="영어 단어 시험 프로그램", 
                              font=("Arial", 20, "bold"), bg="#ffffff", fg="#333333")
        title_label.pack(pady=(0, 30))
        
        # 안내 메시지
        info_label = tk.Label(main_frame, 
                             text="마크다운(.md) 단어 파일을\n여기로 드래그 앤 드롭 하세요!",
                             font=("Arial", 14), bg="#ffffff", fg="#666666")
        info_label.pack(pady=20)
        
        # 드래그 영역 표시
        drop_frame = tk.Frame(main_frame, bg="#f8f9fa", relief="ridge", borderwidth=2)
        drop_frame.pack(fill="both", expand=True, pady=20)
        
        drop_label = tk.Label(drop_frame, text="📁\n드래그 앤 드롭 영역", 
                             font=("Arial", 16), bg="#f8f9fa", fg="#6c757d")
        drop_label.pack(expand=True)
        
        # 선택된 파일 표시
        self.file_label = tk.Label(main_frame, text="", 
                                  font=("Arial", 12), bg="#ffffff", fg="#007acc")
        self.file_label.pack(pady=10)
        
        # API 키 상태 표시
        api_status = self._check_api_key()
        status_color = "#28a745" if api_status else "#dc3545"
        status_text = "✅ API 키 설정됨" if api_status else "❌ API 키 없음 (.env 파일에 설정 필요)"
        
        status_label = tk.Label(main_frame, text=status_text, 
                               font=("Arial", 10), bg="#ffffff", fg=status_color)
        status_label.pack(pady=(20, 0))
    
    def _check_api_key(self) -> bool:
        """API 키 설정 여부를 확인합니다."""
        api_key = os.getenv('OPENAI_API_KEY')
        return bool(api_key and api_key.strip())
    
    def _setup_drag_drop(self):
        """드래그 앤 드롭을 설정합니다."""
        try:
            from tkinterdnd2 import DND_FILES
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self._on_drop)
            logger.info("드래그 앤 드롭 기능이 설정되었습니다.")
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
            messagebox.showerror("파일 형식 오류", "마크다운(.md) 또는 텍스트(.txt) 파일만 지원합니다.")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("파일 없음", f"파일을 찾을 수 없습니다: {file_path}")
            return
        
        self.file_label.config(text=f"선택된 파일: {os.path.basename(file_path)}")
        logger.info(f"드래그앤드롭으로 파일 선택됨: {file_path}")
        
        # 잠시 후 시험 시작
        self.root.after(500, lambda: self.start_test_flow(file_path))
    
    def start_test_flow(self, file_path: str):
        """시험 프로세스를 시작합니다."""
        logger.info(f"시험 시작: {file_path}")
        
        try:
            # 1. 단어 추출
            words = MarkdownParser.parse_words_from_file(file_path)
            if not words:
                messagebox.showerror("오류", "파일에서 단어를 추출할 수 없습니다.")
                return
            
            logger.info(f"단어 추출 완료: {len(words)}개")
            
            # 2. 단어 섞기
            random.shuffle(words)
            
            # 3. 시험 실행
            test_window = WordTestWindow(words)
            user_answers = test_window.run()
            
            if user_answers is None:
                logger.info("사용자가 시험을 취소했습니다.")
                return
            
            logger.info(f"답안 개수: {len(user_answers)}")
            
            # 채점 진행 알림
            messagebox.showinfo("채점 중", "답안을 채점하고 있습니다. 잠시만 기다려주세요...")
            
            # 4. GPT 채점
            gpt_result = self.openai_service.grade_test(words, user_answers)
            
            # 5. 결과 표시
            date_str = os.path.splitext(os.path.basename(file_path))[0]
            test_result = TestResult(words, user_answers, gpt_result, date_str)
            
            result_window = ResultWindow(test_result)
            result_window.run()
            
            # 파일 레이블 초기화
            self.file_label.config(text="")
            
        except Exception as e:
            error_msg = f"프로그램 실행 중 오류가 발생했습니다:\n{e}"
            logger.error(error_msg)
            messagebox.showerror("오류", error_msg)
    
    def run(self):
        """애플리케이션을 실행합니다."""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"프로그램 실행 중 오류: {e}")
            messagebox.showerror("치명적 오류", f"프로그램 실행 중 치명적 오류가 발생했습니다:\n{e}")

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
