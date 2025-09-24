"""
브로커 기본 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, date

class BaseBroker(ABC):
    """브로커 기본 인터페이스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'Unknown')
        self.api_type = config.get('api_type', 'unknown')
        self.enabled = config.get('enabled', False)
        self.connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """브로커 연결"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """브로커 연결 해제"""
        pass
    
    @abstractmethod
    def get_accounts(self) -> List[Dict[str, Any]]:
        """계좌 목록 조회"""
        pass
    
    @abstractmethod
    def get_balance(self, account_number: str) -> Dict[str, Any]:
        """계좌 잔고 조회"""
        pass
    
    @abstractmethod
    def get_holdings(self, account_number: str) -> List[Dict[str, Any]]:
        """보유종목 조회"""
        pass
    
    @abstractmethod
    def get_transactions(self, account_number: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """거래내역 조회"""
        pass
    
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        return self.connected
    
    def get_broker_info(self) -> Dict[str, Any]:
        """브로커 정보 반환"""
        return {
            'name': self.name,
            'api_type': self.api_type,
            'enabled': self.enabled,
            'connected': self.connected
        }
