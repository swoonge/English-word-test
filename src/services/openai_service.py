"""
OpenAI API 서비스 모듈
"""
import os
import logging
from typing import List, Dict
from openai import OpenAI

from ..core.models import WordPair
from ..core.config import Config

logger = logging.getLogger(__name__)


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
