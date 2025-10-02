"""
데이터베이스 현황 확인 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.database import db_manager, get_database_url
from app.utils.config import ConfigManager
from app.models.broker import Broker
from app.models.account import Account
from app.models.balance import DailyBalance
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.models.aggregation import MonthlySummary, StockPerformance, PortfolioAnalysis

def main():
    """데이터베이스 현황 확인"""
    try:
        # 데이터베이스 연결
        config_manager = ConfigManager()
        config = config_manager.config
        database_config = config.get('database', {})
        database_url = get_database_url(database_config)
        db_manager.init_database(database_url)
        
        # 데이터 조회
        session = db_manager.get_session()
        
        print('=== 데이터베이스 현황 ===')
        print(f'증권사 수: {session.query(Broker).count()}')
        print(f'계좌 수: {session.query(Account).count()}')
        print(f'잔고 기록 수: {session.query(DailyBalance).count()}')
        print(f'보유종목 수: {session.query(Holding).count()}')
        print(f'거래내역 수: {session.query(Transaction).count()}')
        print(f'월별 요약 수: {session.query(MonthlySummary).count()}')
        print(f'종목 성과 수: {session.query(StockPerformance).count()}')
        print(f'포트폴리오 분석 수: {session.query(PortfolioAnalysis).count()}')
        
        # 증권사 목록
        brokers = session.query(Broker).all()
        print('\n=== 증권사 목록 ===')
        for broker in brokers:
            print(f'ID: {broker.id}, 이름: {broker.name}, API: {broker.api_type}, 활성: {broker.is_active}')
        
        # 계좌 목록
        accounts = session.query(Account).all()
        print('\n=== 계좌 목록 ===')
        for account in accounts:
            print(f'ID: {account.id}, 증권사: {account.broker.name}, 계좌번호: {account.account_number}, 계좌명: {account.account_name}, 활성: {account.is_active}')
        
        # 최근 잔고 기록
        recent_balances = session.query(DailyBalance).order_by(DailyBalance.balance_date.desc()).limit(5).all()
        print('\n=== 최근 잔고 기록 (5건) ===')
        for balance in recent_balances:
            print(f'계좌ID: {balance.account_id}, 날짜: {balance.balance_date}, 총자산: {balance.total_balance:,.0f}원, 수익률: {balance.profit_loss_rate:.2f}%')
        
        # 보유종목
        holdings = session.query(Holding).all()
        print('\n=== 보유종목 ===')
        for holding in holdings:
            print(f'계좌ID: {holding.account_id}, 종목: {holding.name}({holding.symbol}), 수량: {holding.quantity}, 평가금액: {holding.evaluation_amount:,.0f}원')
        
        # 최근 거래내역
        recent_transactions = session.query(Transaction).order_by(Transaction.transaction_date.desc()).limit(5).all()
        print('\n=== 최근 거래내역 (5건) ===')
        for transaction in recent_transactions:
            print(f'계좌ID: {transaction.account_id}, 날짜: {transaction.transaction_date}, 종목: {transaction.name}({transaction.symbol}), 구분: {transaction.transaction_type}, 수량: {transaction.quantity}, 금액: {transaction.amount:,.0f}원')
        
        session.close()
        print('\n데이터베이스 확인 완료')
        
    except Exception as e:
        print(f'오류 발생: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
