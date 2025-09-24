"""
토큰 파일 관리 클래스
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

class TokenManager:
    """토큰 파일 관리 클래스"""
    
    def __init__(self, broker_name: str = None):
        self.broker_name = broker_name
        self.token_file_path = self._get_token_file_path()
        self.tokens = {}
        self._ensure_token_file()
        self._load_tokens()
    
    def _get_token_file_path(self) -> str:
        """증권사별 토큰 파일 경로 생성"""
        if self.broker_name:
            # 특정 증권사의 토큰 파일
            return f"./token/{self.broker_name.lower()}/tokens.json"
        else:
            # 전체 토큰 파일 (레거시 지원)
            return "./token/tokens.json"
    
    def _ensure_token_file(self):
        """토큰 파일 디렉토리 생성"""
        os.makedirs(os.path.dirname(self.token_file_path), exist_ok=True)
        
        # 토큰 파일이 없으면 빈 파일 생성
        if not os.path.exists(self.token_file_path):
            with open(self.token_file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
            logger.info(f"토큰 파일이 생성되었습니다: {self.token_file_path}")
    
    def _load_tokens(self):
        """토큰 파일에서 토큰 정보 로드"""
        try:
            with open(self.token_file_path, 'r', encoding='utf-8') as f:
                self.tokens = json.load(f)
            logger.debug("토큰 정보를 로드했습니다.")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"토큰 파일 로드 실패: {str(e)}")
            self.tokens = {}
    
    def _save_tokens(self):
        """토큰 정보를 파일에 저장"""
        try:
            with open(self.token_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.tokens, f, indent=2, ensure_ascii=False)
            logger.debug("토큰 정보를 저장했습니다.")
        except Exception as e:
            logger.error(f"토큰 파일 저장 실패: {str(e)}")
            raise
    
    def save_token(self, access_token: str, refresh_token: str = None, 
                   expires_in: int = 86400):
        """토큰 정보 저장"""
        try:
            # 만료 시간 계산 (현재 시간 + expires_in 초)
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            token_info = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': expires_at.isoformat(),
                'created_at': datetime.now().isoformat(),
                'expires_in': expires_in
            }
            
            # 증권사별 토큰 저장
            self.tokens['current'] = token_info
            self._save_tokens()
            
            logger.info(f"브로커 {self.broker_name}의 토큰이 저장되었습니다.")
            logger.info(f"토큰 만료 시간: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"토큰 저장 실패: {str(e)}")
            raise
    
    def get_token(self) -> Optional[Dict[str, Any]]:
        """토큰 정보 조회"""
        return self.tokens.get('current')
    
    def get_access_token(self) -> Optional[str]:
        """액세스 토큰 조회"""
        token_info = self.get_token()
        if token_info:
            return token_info.get('access_token')
        return None
    
    def get_refresh_token(self) -> Optional[str]:
        """리프레시 토큰 조회"""
        token_info = self.get_token()
        if token_info:
            return token_info.get('refresh_token')
        return None
    
    def is_token_expired(self, threshold_seconds: int = 300) -> bool:
        """토큰 만료 여부 확인"""
        token_info = self.get_token()
        if not token_info:
            return True
        
        try:
            expires_at = datetime.fromisoformat(token_info.get('expires_at', ''))
            # 임계값 시간 전에 만료로 간주
            threshold_time = datetime.now() + timedelta(seconds=threshold_seconds)
            return expires_at <= threshold_time
        except (ValueError, TypeError):
            logger.warning(f"브로커 {self.broker_name}의 토큰 만료 시간을 파싱할 수 없습니다.")
            return True
    
    def is_token_valid(self) -> bool:
        """토큰 유효성 확인"""
        token_info = self.get_token()
        if not token_info:
            return False
        
        return not self.is_token_expired()
    
    def get_token_expiry_info(self) -> Optional[Dict[str, Any]]:
        """토큰 만료 정보 조회"""
        token_info = self.get_token()
        if not token_info:
            return None
        
        try:
            expires_at = datetime.fromisoformat(token_info.get('expires_at', ''))
            created_at = datetime.fromisoformat(token_info.get('created_at', ''))
            
            return {
                'created_at': created_at,
                'expires_at': expires_at,
                'is_expired': self.is_token_expired(),
                'is_valid': self.is_token_valid(),
                'expires_in_seconds': (expires_at - datetime.now()).total_seconds(),
                'expires_in_hours': (expires_at - datetime.now()).total_seconds() / 3600
            }
        except (ValueError, TypeError):
            return None
    
    def delete_token(self):
        """토큰 삭제"""
        if 'current' in self.tokens:
            del self.tokens['current']
            self._save_tokens()
            logger.info(f"브로커 {self.broker_name}의 토큰이 삭제되었습니다.")
    
    def clear_all_tokens(self):
        """모든 토큰 삭제"""
        self.tokens = {}
        self._save_tokens()
        logger.info(f"브로커 {self.broker_name}의 모든 토큰이 삭제되었습니다.")
    
    def list_tokens(self) -> Dict[str, Dict[str, Any]]:
        """저장된 토큰 정보 조회"""
        result = {}
        if 'current' in self.tokens:
            result['current'] = self.get_token_expiry_info()
        return result
