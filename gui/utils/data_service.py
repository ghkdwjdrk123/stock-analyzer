"""
GUI용 데이터 서비스
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.database import db_manager, get_database_url
from app.models.account import Account
from app.models.balance import DailyBalance
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.models.broker import Broker
from app.models.aggregation import MonthlySummary, StockPerformance, PortfolioAnalysis
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DataService:
    """GUI용 데이터 서비스"""
    
    def __init__(self):
        self.session = None
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            from app.utils.config import ConfigManager
            config_manager = ConfigManager()
            config = config_manager.config
            database_config = config.get('database', {})
            database_url = get_database_url(database_config)
            db_manager.init_database(database_url)
            logger.info("데이터베이스 초기화 완료")
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {str(e)}")
    
    def _get_session(self) -> Session:
        """데이터베이스 세션 가져오기"""
        if not self.session:
            self.session = db_manager.get_session()
        return self.session
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """계좌 목록 조회"""
        try:
            session = self._get_session()

            # 모든 계좌 조회 (활성/비활성 구분 없이) - JOIN 없이 조회
            accounts = session.query(Account).all()

            result = []
            for acc in accounts:
                try:
                    # 브로커 정보를 별도로 조회
                    broker = session.query(Broker).filter(Broker.id == acc.broker_id).first()
                    broker_name = broker.name if broker else 'Unknown'

                    result.append({
                        'id': acc.id,
                        'broker_id': acc.broker_id,
                        'broker_name': broker_name,
                        'account_number': acc.account_number,
                        'account_name': acc.account_name or '',
                        'account_type': acc.account_type,
                        'is_active': acc.is_active,
                        'created_at': acc.created_at.isoformat() if acc.created_at else None
                    })
                except Exception as e:
                    logger.warning(f"계좌 {acc.id} 처리 중 오류: {str(e)}")
                    continue

            return result

        except Exception as e:
            logger.error(f"계좌 목록 조회 실패: {str(e)}")
            return []

    def get_active_accounts(self) -> List[Dict[str, Any]]:
        """활성 계좌 목록 조회 (is_active=True)"""
        try:
            session = self._get_session()

            # 활성 상태인 계좌만 조회
            accounts = session.query(Account).filter(Account.is_active == True).all()

            result = []
            for acc in accounts:
                try:
                    # 브로커 정보를 별도로 조회
                    broker = session.query(Broker).filter(Broker.id == acc.broker_id).first()
                    broker_name = broker.name if broker else 'Unknown'

                    result.append({
                        'id': acc.id,
                        'broker_id': acc.broker_id,
                        'broker_name': broker_name,
                        'account_number': acc.account_number,
                        'account_name': acc.account_name or '',
                        'account_type': acc.account_type,
                        'is_active': acc.is_active,
                        'created_at': acc.created_at.isoformat() if acc.created_at else None
                    })
                except Exception as e:
                    logger.warning(f"계좌 {acc.id} 처리 중 오류: {str(e)}")
                    continue

            return result

        except Exception as e:
            logger.error(f"활성 계좌 목록 조회 실패: {str(e)}")
            return []
    
    def get_latest_balance(self, account_id: int) -> Optional[Dict[str, Any]]:
        """최신 잔고 정보 조회"""
        try:
            session = self._get_session()
            
            balance = session.query(DailyBalance).filter(
                DailyBalance.account_id == account_id
            ).order_by(desc(DailyBalance.balance_date)).first()
            
            if balance:
                return {
                    'balance_date': balance.balance_date.isoformat(),
                    'total_balance': float(balance.total_balance or 0),
                    'cash_balance': float(balance.cash_balance or 0),
                    'stock_balance': float(balance.stock_balance or 0),
                    'evaluation_amount': float(balance.evaluation_amount or 0),
                    'profit_loss': float(balance.profit_loss or 0),
                    'profit_loss_rate': float(balance.profit_loss_rate or 0)
                }
            return None
            
        except Exception as e:
            logger.error(f"최신 잔고 조회 실패: {str(e)}")
            return None
    
    def get_balance_history(self, account_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """잔고 이력 조회 (날짜별 최신 데이터만)"""
        try:
            session = self._get_session()

            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            # 각 날짜별로 가장 최신 업데이트된 데이터만 조회
            from sqlalchemy import func

            # 서브쿼리: 각 날짜별 최신 updated_at 조회
            latest_updates = session.query(
                DailyBalance.balance_date,
                func.max(DailyBalance.updated_at).label('max_updated_at')
            ).filter(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date >= start_date,
                    DailyBalance.balance_date <= end_date
                )
            ).group_by(DailyBalance.balance_date).subquery()

            # 메인 쿼리: 최신 데이터만 조회
            balances = session.query(DailyBalance).join(
                latest_updates,
                and_(
                    DailyBalance.balance_date == latest_updates.c.balance_date,
                    DailyBalance.updated_at == latest_updates.c.max_updated_at
                )
            ).filter(
                DailyBalance.account_id == account_id
            ).order_by(desc(DailyBalance.balance_date)).all()

            return [{
                'balance_date': balance.balance_date.isoformat(),
                'total_balance': float(balance.total_balance),
                'cash_balance': float(balance.cash_balance),
                'stock_balance': float(balance.stock_balance),
                'evaluation_amount': float(balance.evaluation_amount),
                'profit_loss': float(balance.profit_loss),
                'profit_loss_rate': float(balance.profit_loss_rate),
                'updated_at': balance.updated_at.isoformat() if balance.updated_at else None
            } for balance in balances]

        except Exception as e:
            logger.error(f"잔고 이력 조회 실패: {str(e)}")
            return []
    
    def get_holdings(self, account_id: int) -> List[Dict[str, Any]]:
        """보유종목 조회 (계좌별 종목의 최신 데이터만)"""
        try:
            session = self._get_session()

            # 계좌별 종목의 최신 업데이트 데이터만 조회 (수량 0인 것 제외)
            from sqlalchemy import func

            # 서브쿼리: 각 종목별 최신 updated_at 조회
            latest_holdings = session.query(
                Holding.symbol,
                func.max(Holding.updated_at).label('max_updated_at')
            ).filter(
                Holding.account_id == account_id
            ).group_by(Holding.symbol).subquery()

            # 메인 쿼리: 최신 데이터만 조회하고 수량이 0보다 큰 것만
            holdings = session.query(Holding).join(
                latest_holdings,
                and_(
                    Holding.symbol == latest_holdings.c.symbol,
                    Holding.updated_at == latest_holdings.c.max_updated_at
                )
            ).filter(
                and_(
                    Holding.account_id == account_id,
                    Holding.quantity > 0  # 실제 보유 중인 종목만
                )
            ).order_by(desc(Holding.evaluation_amount)).all()

            result = []
            for holding in holdings:
                try:
                    result.append({
                        'symbol': holding.symbol or '',
                        'name': holding.name or '',
                        'quantity': holding.quantity or 0,
                        'average_price': float(holding.average_price or 0),
                        'current_price': float(holding.current_price or 0),
                        'evaluation_amount': float(holding.evaluation_amount or 0),
                        'profit_loss': float(holding.profit_loss or 0),
                        'profit_loss_rate': float(holding.profit_loss_rate or 0),
                        'last_updated': holding.last_updated.isoformat() if holding.last_updated else None,
                        'updated_at': holding.updated_at.isoformat() if holding.updated_at else None
                    })
                except Exception as e:
                    logger.warning(f"보유종목 {holding.symbol} 처리 중 오류: {str(e)}")
                    continue

            return result

        except Exception as e:
            logger.error(f"보유종목 조회 실패: {str(e)}")
            return []
    
    def get_transactions(self, account_id: int, **filters) -> List[Dict[str, Any]]:
        """거래내역 조회"""
        try:
            session = self._get_session()
            
            query = session.query(Transaction).filter(
                Transaction.account_id == account_id
            )
            
            # 날짜 필터
            if 'start_date' in filters:
                query = query.filter(Transaction.transaction_date >= filters['start_date'])
            if 'end_date' in filters:
                query = query.filter(Transaction.transaction_date <= filters['end_date'])
            
            # 거래 유형 필터
            if 'transaction_type' in filters and filters['transaction_type'] != '전체':
                query = query.filter(Transaction.transaction_type == filters['transaction_type'])
            
            # 종목 필터
            if 'symbol' in filters and filters['symbol']:
                symbol_filter = filters['symbol']
                query = query.filter(
                    or_(
                        Transaction.symbol.contains(symbol_filter),
                        Transaction.name.contains(symbol_filter)
                    )
                )
            
            transactions = query.order_by(desc(Transaction.transaction_date)).all()
            
            result = []
            for transaction in transactions:
                try:
                    result.append({
                        'transaction_date': transaction.transaction_date.isoformat(),
                        'symbol': transaction.symbol or '',
                        'name': transaction.name or '',
                        'transaction_type': transaction.transaction_type or '',
                        'quantity': transaction.quantity or 0,
                        'price': float(transaction.price or 0),
                        'amount': float(transaction.amount or 0),
                        'fee': float(transaction.fee or 0)
                    })
                except Exception as e:
                    logger.warning(f"거래내역 {transaction.id} 처리 중 오류: {str(e)}")
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"거래내역 조회 실패: {str(e)}")
            return []
    
    def get_recent_transactions(self, account_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 거래내역 조회"""
        try:
            session = self._get_session()
            
            transactions = session.query(Transaction).filter(
                Transaction.account_id == account_id
            ).order_by(desc(Transaction.transaction_date)).limit(limit).all()
            
            return [{
                'transaction_date': transaction.transaction_date.isoformat(),
                'symbol': transaction.symbol,
                'name': transaction.name,
                'transaction_type': transaction.transaction_type,
                'quantity': transaction.quantity,
                'price': float(transaction.price),
                'amount': float(transaction.amount),
                'fee': float(transaction.fee)
            } for transaction in transactions]
            
        except Exception as e:
            logger.error(f"최근 거래내역 조회 실패: {str(e)}")
            return []
    
    def has_today_data(self, account_id: int) -> bool:
        """당일 데이터 존재 여부 확인"""
        try:
            session = self._get_session()

            today = date.today()

            # 당일 잔고 데이터 확인
            today_balance = session.query(DailyBalance).filter(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date == today
                )
            ).first()

            return today_balance is not None

        except Exception as e:
            logger.error(f"당일 데이터 확인 실패: {str(e)}")
            return False

    def check_all_accounts_today_data(self) -> Dict[str, bool]:
        """모든 활성 계좌의 당일 데이터 존재 여부 확인"""
        try:
            accounts = self.get_active_accounts()  # 활성 계좌만 확인
            result = {}

            for account in accounts:
                account_id = account['id']
                has_data = self.has_today_data(account_id)
                result[account_id] = has_data

            return result

        except Exception as e:
            logger.error(f"전체 활성 계좌 당일 데이터 확인 실패: {str(e)}")
            return {}

    def has_any_missing_today_data(self) -> bool:
        """활성 계좌 중 당일 데이터가 없는 계좌가 있는지 확인"""
        try:
            today_data_status = self.check_all_accounts_today_data()

            # 하나라도 False가 있으면 True 반환 (누락된 데이터가 있음)
            return not all(today_data_status.values()) if today_data_status else True

        except Exception as e:
            logger.error(f"당일 데이터 누락 확인 실패: {str(e)}")
            return True  # 에러 시 안전하게 True 반환

    def collect_all_active_accounts_data(self) -> Dict[str, Any]:
        """모든 활성 계좌의 데이터 수집 수행"""
        try:
            from app.services.broker_service import BrokerService
            from app.services.data_collector import DataCollector
            from app.utils.config import ConfigManager

            config_manager = ConfigManager()
            broker_service = BrokerService(config_manager.config)
            data_collector = DataCollector(broker_service)

            # 활성 계좌 목록 조회
            active_accounts = self.get_active_accounts()

            if not active_accounts:
                return {
                    'success': False,
                    'message': '활성 계좌가 없습니다.',
                    'collected_count': 0,
                    'total_count': 0
                }

            collected_count = 0
            failed_accounts = []

            # 각 활성 계좌의 데이터 수집
            for account in active_accounts:
                try:
                    data_collector.collect_account_data(
                        account['broker_name'],
                        account['account_number']
                    )
                    collected_count += 1
                    logger.info(f"계좌 {account['account_number']} 데이터 수집 완료")

                except Exception as e:
                    failed_accounts.append({
                        'account_number': account['account_number'],
                        'broker_name': account['broker_name'],
                        'error': str(e)
                    })
                    logger.error(f"계좌 {account['account_number']} 데이터 수집 실패: {str(e)}")

            # 결과 반환
            success = collected_count > 0
            total_count = len(active_accounts)

            result = {
                'success': success,
                'collected_count': collected_count,
                'total_count': total_count,
                'failed_accounts': failed_accounts
            }

            if success:
                if collected_count == total_count:
                    result['message'] = f'✅ 모든 계좌({total_count}개) 데이터 수집 완료'
                else:
                    result['message'] = f'⚠️ {collected_count}/{total_count}개 계좌 데이터 수집 완료'
            else:
                result['message'] = '❌ 모든 계좌 데이터 수집 실패'

            return result

        except Exception as e:
            logger.error(f"전체 활성 계좌 데이터 수집 실패: {str(e)}")
            return {
                'success': False,
                'message': f'❌ 데이터 수집 중 오류 발생: {str(e)}',
                'collected_count': 0,
                'total_count': 0,
                'failed_accounts': []
            }

    def close_session(self):
        """세션 종료"""
        if self.session:
            self.session.close()
            self.session = None
