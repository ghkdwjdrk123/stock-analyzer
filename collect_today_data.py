"""
오늘자 데이터 수집 스크립트
"""
import os
import sys
from pathlib import Path
from datetime import datetime, date

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.config import ConfigManager
from app.utils.database import db_manager, get_database_url
from app.utils.logger import setup_logging, get_logger
from app.services.broker_service import BrokerService

# 모델들을 직접 import
from app.models.broker import Broker
from app.models.account import Account
from app.models.balance import DailyBalance
from app.models.holding import Holding
from app.models.transaction import Transaction

def main():
    """오늘자 데이터 수집"""
    try:
        print("=== 오늘자 데이터 수집 시작 ===")

        # 설정 로드
        config_manager = ConfigManager()
        config = config_manager.config

        # 로깅 설정
        setup_logging(config)
        logger = get_logger(__name__)

        # 데이터베이스 초기화
        database_config = config.get('database', {})
        database_url = get_database_url(database_config)
        db_manager.init_database(database_url)

        # 브로커 서비스 초기화
        broker_service = BrokerService(config)

        # 한국투자증권 브로커 가져오기
        kis_broker = broker_service.get_broker("한국투자증권")
        if not kis_broker:
            print("ERROR: 한국투자증권 브로커를 찾을 수 없습니다.")
            return

        # API 연결
        if not kis_broker.is_connected():
            kis_broker.connect()

        # 계좌 목록 조회
        accounts = kis_broker.get_accounts()
        print(f"조회된 계좌 수: {len(accounts)}")

        if not accounts:
            print("ERROR: 조회된 계좌가 없습니다.")
            return

        # 세션 생성
        session = db_manager.get_session()

        try:
            for account_info in accounts:
                account_number = account_info.get('account_number')
                print(f"\n계좌 {account_number} 데이터 수집 중...")

                # 1. 브로커 정보 확인/생성
                broker = session.query(Broker).filter(Broker.name == "한국투자증권").first()
                if not broker:
                    broker = Broker(
                        name="한국투자증권",
                        api_type="kis",
                        platform="cross",
                        enabled=True,
                        description="한국투자증권 API"
                    )
                    session.add(broker)
                    session.flush()

                # 2. 계좌 정보 확인/생성
                account = session.query(Account).filter(
                    Account.account_number == account_number
                ).first()

                if not account:
                    account = Account(
                        broker_id=broker.id,
                        account_number=account_number,
                        account_name=account_info.get('account_name', ''),
                        account_type=account_info.get('account_type', 'NORMAL'),
                        is_active=True
                    )
                    session.add(account)
                    session.flush()

                # 3. 잔고 정보 수집 및 저장 (UPSERT 방식)
                balance_info = kis_broker.get_balance(account_number)
                today = date.today()

                # 오늘자 잔고 데이터 UPSERT
                existing_balance = session.query(DailyBalance).filter(
                    DailyBalance.account_id == account.id,
                    DailyBalance.balance_date == today
                ).first()

                balance_data = {
                    'cash_balance': balance_info.get('cash_balance', 0),
                    'stock_balance': balance_info.get('stock_balance', 0),
                    'total_balance': balance_info.get('total_balance', 0),
                    'evaluation_amount': balance_info.get('evaluation_amount', 0),
                    'profit_loss': balance_info.get('profit_loss', 0),
                    'profit_loss_rate': balance_info.get('profit_loss_rate', 0)
                }

                if existing_balance:
                    # 기존 데이터 업데이트
                    for key, value in balance_data.items():
                        setattr(existing_balance, key, value)
                    existing_balance.updated_at = datetime.utcnow()
                    print(f"잔고 데이터 업데이트: {existing_balance.total_balance:,.0f}원")
                else:
                    # 새 데이터 추가
                    new_balance = DailyBalance(
                        account_id=account.id,
                        balance_date=today,
                        **balance_data
                    )
                    session.add(new_balance)
                    print(f"잔고 데이터 추가: {new_balance.total_balance:,.0f}원")

                # 4. 보유종목 정보 수집 및 저장 (UPSERT 방식)
                holdings_info = kis_broker.get_holdings(account_number)
                print(f"보유종목 {len(holdings_info)}개 처리 중...")

                for holding_data in holdings_info:
                    symbol = holding_data.get('symbol')

                    # 기존 보유종목 확인 (계좌별 종목 고유성 보장)
                    existing_holding = session.query(Holding).filter(
                        Holding.account_id == account.id,
                        Holding.symbol == symbol
                    ).first()

                    holding_update_data = {
                        'name': holding_data.get('name', ''),
                        'quantity': holding_data.get('quantity', 0),
                        'average_price': holding_data.get('average_price', 0),
                        'current_price': holding_data.get('current_price', 0),
                        'evaluation_amount': holding_data.get('evaluation_amount', 0),
                        'profit_loss': holding_data.get('profit_loss', 0),
                        'profit_loss_rate': holding_data.get('profit_loss_rate', 0),
                        'last_updated': datetime.utcnow()
                    }

                    if existing_holding:
                        # 기존 데이터 업데이트
                        for key, value in holding_update_data.items():
                            setattr(existing_holding, key, value)
                        existing_holding.updated_at = datetime.utcnow()
                    else:
                        # 새 데이터 추가
                        new_holding = Holding(
                            account_id=account.id,
                            symbol=symbol,
                            **holding_update_data
                        )
                        session.add(new_holding)

                print(f"계좌 {account_number} 데이터 수집 완료")

            # 모든 변경사항 커밋
            session.commit()
            print("\n모든 데이터 수집 및 저장 완료!")

        except Exception as e:
            session.rollback()
            print(f"데이터 저장 중 오류 발생: {str(e)}")
            raise
        finally:
            session.close()

        # 브로커 연결 해제
        kis_broker.disconnect()

    except Exception as e:
        print(f"전체 작업 실패: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()