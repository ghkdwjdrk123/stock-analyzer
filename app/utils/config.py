"""
설정 관리 클래스
"""
import json
import os
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
from app.utils.exceptions import ConfigurationError

class ConfigManager:
    """설정 관리 클래스"""
    
    def __init__(self, config_path: str = "./config/config.json"):
        self.config_path = config_path
        
        # env 파일 로드
        load_dotenv('env')
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 환경변수로 설정 오버라이드
            self._apply_env_overrides(config)
            
            # 설정 검증
            self._validate_config(config)
            
            return config
        except FileNotFoundError:
            raise ConfigurationError(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"설정 파일 JSON 형식 오류: {e}")
    
    def _apply_env_overrides(self, config: Dict[str, Any]):
        """환경변수로 설정 오버라이드"""
        if os.getenv('DATABASE_TYPE'):
            config.setdefault('database', {})['type'] = os.getenv('DATABASE_TYPE')
        
        if os.getenv('LOG_LEVEL'):
            config.setdefault('logging', {})['level'] = os.getenv('LOG_LEVEL')
        
        if os.getenv('KIS_APP_KEY'):
            # 한국투자증권 설정 업데이트
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('credentials', {})['app_key'] = os.getenv('KIS_APP_KEY')
                    break
        
        if os.getenv('KIS_APP_SECRET'):
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('credentials', {})['app_secret'] = os.getenv('KIS_APP_SECRET')
                    break
        
        # 이메일 설정 오버라이드
        if os.getenv('EMAIL_USERNAME'):
            config.setdefault('notifications', {}).setdefault('email', {})['username'] = os.getenv('EMAIL_USERNAME')
        
        if os.getenv('EMAIL_PASSWORD'):
            config.setdefault('notifications', {}).setdefault('email', {})['password'] = os.getenv('EMAIL_PASSWORD')
        
        # 한국투자증권 API 설정 오버라이드
        if os.getenv('KIS_BASE_URL'):
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('api_settings', {})['base_url'] = os.getenv('KIS_BASE_URL')
                    break
        
        if os.getenv('KIS_TR_ID_BALANCE'):
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('api_settings', {})['tr_id_balance'] = os.getenv('KIS_TR_ID_BALANCE')
                    break
        
        
        if os.getenv('KIS_ACCOUNT_PRODUCT_CODE'):
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('api_settings', {})['account_product_code'] = os.getenv('KIS_ACCOUNT_PRODUCT_CODE')
                    break
        
        if os.getenv('KIS_MARKET_DIV_CODE'):
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('api_settings', {})['market_div_code'] = os.getenv('KIS_MARKET_DIV_CODE')
                    break
        
        # 한국투자증권 계좌 정보 오버라이드
        if os.getenv('KIS_ACCOUNT_8_PROD'):
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('api_settings', {})['account_8_prod'] = os.getenv('KIS_ACCOUNT_8_PROD')
                    break
        
        if os.getenv('KIS_ACCOUNT_PD_PROD'):
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('api_settings', {})['account_pd_prod'] = os.getenv('KIS_ACCOUNT_PD_PROD')
                    break
        
        # 한국투자증권 API 엔드포인트 오버라이드
        if os.getenv('KIS_API_BALANCE'):
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('api_settings', {})['api_balance'] = os.getenv('KIS_API_BALANCE')
                    break
        
        if os.getenv('KIS_API_ACCOUNTS'):
            for broker in config.get('brokers', []):
                if broker.get('api_type') == 'kis':
                    broker.setdefault('api_settings', {})['api_accounts'] = os.getenv('KIS_API_ACCOUNTS')
                    break
    
    def _validate_config(self, config: Dict[str, Any]):
        """설정 검증"""
        schema = {
            "type": "object",
            "required": ["scheduler", "database", "brokers"],
            "properties": {
                "scheduler": {
                    "type": "object",
                    "required": ["enabled", "cron_expression"],
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "cron_expression": {"type": "string"},
                        "timezone": {"type": "string"}
                    }
                },
                "database": {
                    "type": "object",
                    "required": ["type"],
                    "properties": {
                        "type": {"enum": ["sqlite", "postgresql"]},
                        "path": {"type": "string"}
                    }
                },
                "brokers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "api_type", "enabled"],
                        "properties": {
                            "name": {"type": "string"},
                            "api_type": {"type": "string"},
                            "enabled": {"type": "boolean"}
                        }
                    }
                }
            }
        }
        
        try:
            validate(instance=config, schema=schema)
        except ValidationError as e:
            raise ConfigurationError(f"설정 파일 검증 실패: {e.message}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 조회"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """설정 값 설정"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self):
        """설정 파일 저장"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_broker_config(self, broker_name: str) -> Optional[Dict[str, Any]]:
        """특정 브로커 설정 조회"""
        for broker in self.config.get('brokers', []):
            if broker.get('name') == broker_name:
                return broker
        return None
