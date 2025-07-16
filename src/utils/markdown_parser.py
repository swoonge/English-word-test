"""
마크다운 파싱 유틸리티
"""
import logging
from typing import List

from ..core.models import WordPair

logger = logging.getLogger(__name__)


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
