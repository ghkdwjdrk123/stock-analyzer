"""
브로커 서비스 클래스
"""
from typing import List, Dict, Any, Optional
from app.brokers.kis_broker import KISBroker
from app.brokers.kiwoom_broker import KiwoomBroker
from app.brokers.base_broker import BaseBroker
from app.utils.exceptions import BrokerError
from app.utils.logger import get_logger

logger = get_logger(__name__)

class BrokerService:
    """브로커 서비스 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.brokers: Dict[str, BaseBroker] = {}
        self._initialize_brokers()
    
    def _initialize_brokers(self):
        """브로커 초기화"""
        brokers_config = self.config.get('brokers', [])
        
        for broker_config in brokers_config:
            if not broker_config.get('enabled', False):
                continue
            
            broker_name = broker_config.get('name')
            api_type = broker_config.get('api_type')
            
            # 디버깅용 로그
            logger.debug(f"브로커 설정 - {broker_name}: {broker_config}")
            
            try:
                if api_type == 'kis':
                    broker = KISBroker(broker_config)
                    self.brokers[broker_name] = broker
                    logger.info(f"브로커 {broker_name} 초기화 완료")
                elif api_type == 'kiwoom':
                    broker = KiwoomBroker(broker_config)
                    self.brokers[broker_name] = broker
                    logger.info(f"브로커 {broker_name} 초기화 완료")
                else:
                    logger.warning(f"지원하지 않는 API 타입: {api_type}")
                    
            except Exception as e:
                logger.error(f"브로커 {broker_name} 초기화 실패: {str(e)}")
    
    def get_broker(self, broker_name: str) -> Optional[BaseBroker]:
        """특정 브로커 반환"""
        return self.brokers.get(broker_name)
    
    def get_all_brokers(self) -> Dict[str, BaseBroker]:
        """모든 브로커 반환"""
        return self.brokers
    
    def connect_broker(self, broker_name: str) -> bool:
        """브로커 연결"""
        broker = self.get_broker(broker_name)
        if not broker:
            raise BrokerError(f"브로커 {broker_name}을 찾을 수 없습니다.")
        
        try:
            return broker.connect()
        except Exception as e:
            logger.error(f"브로커 {broker_name} 연결 실패: {str(e)}")
            raise BrokerError(f"브로커 연결 실패: {str(e)}")
    
    def disconnect_broker(self, broker_name: str) -> bool:
        """브로커 연결 해제"""
        broker = self.get_broker(broker_name)
        if not broker:
            raise BrokerError(f"브로커 {broker_name}을 찾을 수 없습니다.")
        
        try:
            return broker.disconnect()
        except Exception as e:
            logger.error(f"브로커 {broker_name} 연결 해제 실패: {str(e)}")
            return False
    
    def get_all_accounts(self) -> List[Dict[str, Any]]:
        """모든 브로커의 계좌 목록 조회"""
        all_accounts = []
        
        for broker_name, broker in self.brokers.items():
            try:
                if not broker.is_connected():
                    broker.connect()
                
                accounts = broker.get_accounts()
                for account in accounts:
                    account['broker_name'] = broker_name
                    all_accounts.append(account)
                    
            except Exception as e:
                logger.error(f"브로커 {broker_name} 계좌 조회 실패: {str(e)}")
                continue
        
        return all_accounts
    
    def get_account_balance(self, broker_name: str, account_number: str) -> Dict[str, Any]:
        """계좌 잔고 조회"""
        broker = self.get_broker(broker_name)
        if not broker:
            raise BrokerError(f"브로커 {broker_name}을 찾을 수 없습니다.")
        
        try:
            if not broker.is_connected():
                broker.connect()
            
            return broker.get_balance(account_number)
            
        except Exception as e:
            logger.error(f"계좌 {account_number} 잔고 조회 실패: {str(e)}")
            raise BrokerError(f"잔고 조회 실패: {str(e)}")
    
    def get_account_holdings(self, broker_name: str, account_number: str) -> List[Dict[str, Any]]:
        """계좌 보유종목 조회"""
        broker = self.get_broker(broker_name)
        if not broker:
            raise BrokerError(f"브로커 {broker_name}을 찾을 수 없습니다.")
        
        try:
            if not broker.is_connected():
                broker.connect()
            
            return broker.get_holdings(account_number)
            
        except Exception as e:
            logger.error(f"계좌 {account_number} 보유종목 조회 실패: {str(e)}")
            raise BrokerError(f"보유종목 조회 실패: {str(e)}")
    
    def get_account_transactions(self, broker_name: str, account_number: str, 
                               start_date, end_date) -> List[Dict[str, Any]]:
        """계좌 거래내역 조회"""
        broker = self.get_broker(broker_name)
        if not broker:
            raise BrokerError(f"브로커 {broker_name}을 찾을 수 없습니다.")
        
        try:
            if not broker.is_connected():
                broker.connect()
            
            return broker.get_transactions(account_number, start_date, end_date)
            
        except Exception as e:
            logger.error(f"계좌 {account_number} 거래내역 조회 실패: {str(e)}")
            raise BrokerError(f"거래내역 조회 실패: {str(e)}")
    
    def close_all_connections(self):
        """모든 브로커 연결 해제"""
        for broker_name, broker in self.brokers.items():
            try:
                broker.disconnect()
                logger.info(f"브로커 {broker_name} 연결 해제 완료")
            except Exception as e:
                logger.error(f"브로커 {broker_name} 연결 해제 실패: {str(e)}")
