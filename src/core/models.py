"""
데이터 모델 정의
"""
from dataclasses import dataclass
from typing import List, Dict, Optional


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
