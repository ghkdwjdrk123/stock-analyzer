"""
한국투자증권 API 테스트 스크립트
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.config import ConfigManager
from app.utils.database import db_manager, get_database_url
from app.utils.logger import setup_logging, get_logger
from app.services.broker_service import BrokerService

def test_kis_api():
    """한국투자증권 API 테스트"""
    try:
        # 설정 로드
        config_manager = ConfigManager()
        config = config_manager.config
        
        # 로깅 설정
        setup_logging(config)
        logger = get_logger(__name__)
        logger.info("한국투자증권 API 테스트를 시작합니다.")
        
        # 데이터베이스 초기화
        database_config = config.get('database', {})
        database_url = get_database_url(database_config)
        db_manager.init_database(database_url)
        logger.info("데이터베이스 초기화 완료")
        
        # 브로커 서비스 초기화
        broker_service = BrokerService(config)
        logger.info("브로커 서비스 초기화 완료")
        
        # 한국투자증권 브로커 가져오기
        kis_broker = broker_service.get_broker("한국투자증권")
        if not kis_broker:
            logger.error("한국투자증권 브로커를 찾을 수 없습니다.")
            return False
        
        # API 연결 테스트
        logger.info("한국투자증권 API 연결을 시도합니다.")
        if not kis_broker.connect():
            logger.error("한국투자증권 API 연결에 실패했습니다.")
            return False
        
        logger.info("한국투자증권 API 연결 성공!")
        
        # 계좌 목록 조회 테스트
        logger.info("계좌 목록 조회를 시도합니다.")
        accounts = kis_broker.get_accounts()
        logger.info(f"조회된 계좌 수: {len(accounts)}")
        
        if not accounts:
            logger.warning("조회된 계좌가 없습니다.")
            return True
        
        # 첫 번째 계좌 정보 출력
        first_account = accounts[0]
        logger.info(f"첫 번째 계좌 정보:")
        logger.info(f"  - 계좌번호: {first_account.get('account_number')}")
        logger.info(f"  - 계좌명: {first_account.get('account_name')}")
        logger.info(f"  - 계좌타입: {first_account.get('account_type')}")
        
        # 잔고 조회 테스트
        account_number = first_account.get('account_number')
        logger.info(f"계좌 {account_number} 잔고 조회를 시도합니다.")
        
        balance = kis_broker.get_balance(account_number)
        logger.info(f"잔고 정보:")
        logger.info(f"  - 현금잔고: {balance.get('cash_balance', 0):,.0f}원")
        logger.info(f"  - 주식잔고: {balance.get('stock_balance', 0):,.0f}원")
        logger.info(f"  - 총잔고: {balance.get('total_balance', 0):,.0f}원")
        logger.info(f"  - 평가금액: {balance.get('evaluation_amount', 0):,.0f}원")
        logger.info(f"  - 손익: {balance.get('profit_loss', 0):,.0f}원")
        logger.info(f"  - 손익률: {balance.get('profit_loss_rate', 0):.2f}%")
        
        # 보유종목 조회 테스트
        logger.info(f"계좌 {account_number} 보유종목 조회를 시도합니다.")
        holdings = kis_broker.get_holdings(account_number)
        logger.info(f"보유종목 수: {len(holdings)}")
        
        if holdings:
            logger.info("보유종목 목록:")
            for i, holding in enumerate(holdings[:5], 1):  # 최대 5개만 출력
                logger.info(f"  {i}. {holding.get('name')} ({holding.get('symbol')})")
                logger.info(f"     수량: {holding.get('quantity'):,}주")
                logger.info(f"     평균단가: {holding.get('average_price', 0):,.0f}원")
                logger.info(f"     현재가: {holding.get('current_price', 0):,.0f}원")
                logger.info(f"     평가금액: {holding.get('evaluation_amount', 0):,.0f}원")
                logger.info(f"     손익: {holding.get('profit_loss', 0):,.0f}원")
                logger.info(f"     손익률: {holding.get('profit_loss_rate', 0):.2f}%")
                logger.info("")
        
        # 종목 가격 조회 테스트 (보유종목 중 하나)
        logger.info("종목 가격 조회 테스트를 시도합니다.")
        try:
            # 보유종목 중 첫 번째 종목으로 테스트
            if holdings:
                test_stock = holdings[0]
                stock_code = test_stock.get('symbol')
                stock_name = test_stock.get('name')
                
                stock_price = kis_broker.get_stock_price(stock_code)
                logger.info(f"{stock_name} ({stock_code}) 가격 정보:")
                logger.info(f"  - 종목명: {stock_price.get('stock_name')}")
                logger.info(f"  - 현재가: {stock_price.get('current_price', 0):,.0f}원")
                logger.info(f"  - 전일대비: {stock_price.get('change_price', 0):,.0f}원")
                logger.info(f"  - 등락률: {stock_price.get('change_rate', 0):.2f}%")
                logger.info(f"  - 보유수량: {stock_price.get('quantity', 0):,}주")
                logger.info(f"  - 평가금액: {stock_price.get('evaluation_amount', 0):,.0f}원")
                logger.info(f"  - 손익: {stock_price.get('profit_loss', 0):,.0f}원")
            else:
                logger.warning("보유종목이 없어 종목 가격 조회 테스트를 건너뜁니다.")
        except Exception as e:
            logger.warning(f"종목 가격 조회 실패: {str(e)}")
        
        # 연결 해제
        kis_broker.disconnect()
        logger.info("한국투자증권 API 연결이 해제되었습니다.")
        
        logger.info("한국투자증권 API 테스트가 성공적으로 완료되었습니다!")
        return True
        
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_kis_api()
    if success:
        print("\nSuccess: 한국투자증권 API 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\nError: 한국투자증권 API 테스트에 실패했습니다.")
        sys.exit(1)
