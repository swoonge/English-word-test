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
        
        # 시스템별 기본값 설정
        self._init_system_defaults()
        
        self.config = self.load_config()
    
    def _init_system_defaults(self):
        """시스템별 기본 설정을 초기화합니다."""
        try:
            from ..utils.system_compatibility import SystemCompatibility
            
            # 시스템별 권장 설정 가져오기
            recommended_font = SystemCompatibility.get_recommended_font()
            recommended_size = SystemCompatibility.get_recommended_font_size()
            theme_rec = SystemCompatibility.get_theme_recommendations()
            
            self.default_config = {
                "ui": {
                    "theme": theme_rec['default_theme'],
                    "font_family": recommended_font,
                    "font_size": recommended_size,
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
            
        except Exception as e:
            logger.warning(f"시스템 호환성 설정 로드 실패, 기본값 사용: {e}")
            # 호환성 모듈 로드 실패 시 기본값 사용
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
            logger.info(f"저장할 config: {config_to_save}")
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            logger.info(f"설정이 {self.config_file}에 저장되었습니다.")
            
            # 저장 후 파일 내용 확인
            with open(self.config_file, 'r', encoding='utf-8') as f:
                saved_content = json.load(f)
            logger.info(f"저장된 파일 내용: {saved_content}")
            
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            import traceback
            logger.error(f"상세 오류: {traceback.format_exc()}")
    
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
    
    def set(self, key_path: str, value):
        """점 표기법으로 설정 값을 설정합니다. 예: 'ui.theme'"""
        keys = key_path.split('.')
        config = self.config
        
        logger.info(f"set 메서드 호출: {key_path} = {value}")
        logger.info(f"변경 전 config 상태: {self.config}")
        
        # 마지막 키 전까지 딕셔너리 생성
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
                logger.info(f"새 딕셔너리 생성: {key}")
            config = config[key]
        
        # 마지막 키에 값 설정
        old_value = config.get(keys[-1], "없음")
        config[keys[-1]] = value
        logger.info(f"설정 변경: {key_path} = {old_value} → {value}")
        logger.info(f"변경 후 config 상태: {self.config}")
