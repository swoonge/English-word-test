"""
시험 결과 창 UI
"""
import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Dict, Tuple, Optional
import logging

from .base_window import BaseWindow
from ..core.config import Config
from ..core.models import TestResult

# pyperclip 클립보드 지원 (선택적)
try:
    import pyperclip
except ImportError:
    pyperclip = None

logger = logging.getLogger(__name__)


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
