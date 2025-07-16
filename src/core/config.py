"""
설정 관리 모듈
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


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
    
    def load_config(self) -> Dict[str, Any]:
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
    
    def save_config(self, config: Dict[str, Any] = None):
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
