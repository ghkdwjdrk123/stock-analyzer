"""
Stock Analyzer 메인 애플리케이션
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.config import ConfigManager
from app.utils.database import db_manager, get_database_url
from app.utils.logger import setup_logging, get_logger
from app.services.broker_service import BrokerService
from app.services.data_collector import DataCollector

# 모델들을 import하여 테이블 생성
from app.models.broker import Broker
from app.models.account import Account
from app.models.balance import DailyBalance
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.models.aggregation import (
    MonthlySummary, StockPerformance, PortfolioAnalysis,
    TradingPattern, RiskMetrics
)

def main():
    """메인 함수"""
    try:
        # 설정 로드
        config_manager = ConfigManager()
        config = config_manager.config
        
        # 로깅 설정
        setup_logging(config)
        logger = get_logger(__name__)
        logger.info("Stock Analyzer 애플리케이션을 시작합니다.")
        
        # 데이터베이스 초기화
        database_config = config.get('database', {})
        database_url = get_database_url(database_config)
        db_manager.init_database(database_url)
        logger.info("데이터베이스 초기화 완료")
        
        # 브로커 서비스 초기화
        broker_service = BrokerService(config)
        logger.info("브로커 서비스 초기화 완료")
        
        # 데이터 수집 서비스 초기화
        data_collector = DataCollector(broker_service)
        logger.info("데이터 수집 서비스 초기화 완료")
        
        # 한국투자증권 브로커 연결 테스트
        kis_broker = broker_service.get_broker("한국투자증권")
        if kis_broker:
            try:
                logger.info("한국투자증권 API 연결을 시도합니다.")
                kis_broker.connect()
                logger.info("한국투자증권 API 연결 성공")
                
                # 계좌 목록 조회 테스트
                accounts = kis_broker.get_accounts()
                logger.info(f"조회된 계좌 수: {len(accounts)}")
                
                for account in accounts:
                    logger.info(f"계좌번호: {account.get('account_number')}, 계좌명: {account.get('account_name')}")
                
                # 첫 번째 계좌의 잔고 조회 테스트
                if accounts:
                    first_account = accounts[0]
                    account_number = first_account.get('account_number')
                    
                    logger.info(f"계좌 {account_number} 잔고 조회를 시도합니다.")
                    balance = kis_broker.get_balance(account_number)
                    logger.info(f"현금잔고: {balance.get('cash_balance', 0):,.0f}원")
                    logger.info(f"주식잔고: {balance.get('stock_balance', 0):,.0f}원")
                    logger.info(f"총잔고: {balance.get('total_balance', 0):,.0f}원")
                    
                    # 보유종목 조회 테스트
                    logger.info(f"계좌 {account_number} 보유종목 조회를 시도합니다.")
                    holdings = kis_broker.get_holdings(account_number)
                    logger.info(f"보유종목 수: {len(holdings)}")
                    
                    for holding in holdings:
                        logger.info(f"종목: {holding.get('name')} ({holding.get('symbol')}), "
                                  f"수량: {holding.get('quantity')}, "
                                  f"평가금액: {holding.get('evaluation_amount', 0):,.0f}원")
                
            except Exception as e:
                logger.error(f"한국투자증권 API 테스트 실패: {str(e)}")
            finally:
                kis_broker.disconnect()
        
        logger.info("Stock Analyzer 애플리케이션이 정상적으로 종료되었습니다.")
        
    except Exception as e:
        logger.error(f"애플리케이션 실행 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
