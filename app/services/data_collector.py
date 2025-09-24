"""
데이터 수집 서비스 클래스
"""
from typing import List, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.services.broker_service import BrokerService
from app.models.account import Account
from app.models.balance import DailyBalance
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.utils.database import db_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DataCollector:
    """데이터 수집 서비스 클래스"""
    
    def __init__(self, broker_service: BrokerService):
        self.broker_service = broker_service
    
    def collect_all_accounts(self):
        """모든 계좌 데이터 수집"""
        try:
            logger.info("전체 계좌 데이터 수집을 시작합니다.")
            
            # 모든 브로커의 계좌 목록 조회
            all_accounts = self.broker_service.get_all_accounts()
            
            for account_info in all_accounts:
                try:
                    self.collect_account_data(
                        account_info['broker_name'],
                        account_info['account_number']
                    )
                except Exception as e:
                    logger.error(f"계좌 {account_info['account_number']} 데이터 수집 실패: {str(e)}")
                    continue
            
            logger.info("전체 계좌 데이터 수집이 완료되었습니다.")
            
        except Exception as e:
            logger.error(f"전체 계좌 데이터 수집 실패: {str(e)}")
            raise
    
    def collect_account_data(self, broker_name: str, account_number: str):
        """특정 계좌 데이터 수집"""
        try:
            logger.info(f"계좌 {account_number} 데이터 수집을 시작합니다.")
            
            # 잔고 정보 수집
            balance_info = self.broker_service.get_account_balance(broker_name, account_number)
            self._save_balance_data(account_number, balance_info)
            
            # 보유종목 정보 수집
            holdings = self.broker_service.get_account_holdings(broker_name, account_number)
            self._save_holdings_data(account_number, holdings)
            
            logger.info(f"계좌 {account_number} 데이터 수집이 완료되었습니다.")
            
        except Exception as e:
            logger.error(f"계좌 {account_number} 데이터 수집 실패: {str(e)}")
            raise
    
    def _save_balance_data(self, account_number: str, balance_info: Dict[str, Any]):
        """잔고 데이터 저장"""
        try:
            session = db_manager.get_session()
            
            # 계좌 ID 조회
            account = session.query(Account).filter(
                Account.account_number == account_number
            ).first()
            
            if not account:
                logger.warning(f"계좌 {account_number}을 찾을 수 없습니다.")
                return
            
            # 오늘 날짜의 잔고 데이터 확인
            today = date.today()
            existing_balance = session.query(DailyBalance).filter(
                DailyBalance.account_id == account.id,
                DailyBalance.balance_date == today
            ).first()
            
            if existing_balance:
                # 기존 데이터 업데이트
                existing_balance.cash_balance = balance_info.get('cash_balance', 0)
                existing_balance.stock_balance = balance_info.get('stock_balance', 0)
                existing_balance.total_balance = balance_info.get('total_balance', 0)
                existing_balance.evaluation_amount = balance_info.get('evaluation_amount', 0)
                existing_balance.profit_loss = balance_info.get('profit_loss', 0)
                existing_balance.profit_loss_rate = balance_info.get('profit_loss_rate', 0)
            else:
                # 새 데이터 생성
                new_balance = DailyBalance(
                    account_id=account.id,
                    balance_date=today,
                    cash_balance=balance_info.get('cash_balance', 0),
                    stock_balance=balance_info.get('stock_balance', 0),
                    total_balance=balance_info.get('total_balance', 0),
                    evaluation_amount=balance_info.get('evaluation_amount', 0),
                    profit_loss=balance_info.get('profit_loss', 0),
                    profit_loss_rate=balance_info.get('profit_loss_rate', 0)
                )
                session.add(new_balance)
            
            session.commit()
            logger.info(f"계좌 {account_number} 잔고 데이터 저장 완료")
            
        except Exception as e:
            session.rollback()
            logger.error(f"잔고 데이터 저장 실패: {str(e)}")
            raise
        finally:
            session.close()
    
    def _save_holdings_data(self, account_number: str, holdings: List[Dict[str, Any]]):
        """보유종목 데이터 저장"""
        try:
            session = db_manager.get_session()
            
            # 계좌 ID 조회
            account = session.query(Account).filter(
                Account.account_number == account_number
            ).first()
            
            if not account:
                logger.warning(f"계좌 {account_number}을 찾을 수 없습니다.")
                return
            
            # 기존 보유종목 데이터 삭제
            session.query(Holding).filter(
                Holding.account_id == account.id
            ).delete()
            
            # 새 보유종목 데이터 저장
            for holding_data in holdings:
                new_holding = Holding(
                    account_id=account.id,
                    symbol=holding_data.get('symbol', ''),
                    name=holding_data.get('name', ''),
                    quantity=holding_data.get('quantity', 0),
                    average_price=holding_data.get('average_price', 0),
                    current_price=holding_data.get('current_price', 0),
                    evaluation_amount=holding_data.get('evaluation_amount', 0),
                    profit_loss=holding_data.get('profit_loss', 0),
                    profit_loss_rate=holding_data.get('profit_loss_rate', 0)
                )
                session.add(new_holding)
            
            session.commit()
            logger.info(f"계좌 {account_number} 보유종목 데이터 저장 완료")
            
        except Exception as e:
            session.rollback()
            logger.error(f"보유종목 데이터 저장 실패: {str(e)}")
            raise
        finally:
            session.close()
    
    def collect_transaction_data(self, broker_name: str, account_number: str, 
                               start_date: date, end_date: date):
        """거래내역 데이터 수집"""
        try:
            logger.info(f"계좌 {account_number} 거래내역 수집을 시작합니다.")
            
            # 거래내역 조회
            transactions = self.broker_service.get_account_transactions(
                broker_name, account_number, start_date, end_date
            )
            
            # 거래내역 데이터 저장
            self._save_transactions_data(account_number, transactions)
            
            logger.info(f"계좌 {account_number} 거래내역 수집이 완료되었습니다.")
            
        except Exception as e:
            logger.error(f"계좌 {account_number} 거래내역 수집 실패: {str(e)}")
            raise
    
    def _save_transactions_data(self, account_number: str, transactions: List[Dict[str, Any]]):
        """거래내역 데이터 저장"""
        try:
            session = db_manager.get_session()
            
            # 계좌 ID 조회
            account = session.query(Account).filter(
                Account.account_number == account_number
            ).first()
            
            if not account:
                logger.warning(f"계좌 {account_number}을 찾을 수 없습니다.")
                return
            
            # 거래내역 데이터 저장
            for transaction_data in transactions:
                new_transaction = Transaction(
                    account_id=account.id,
                    transaction_date=transaction_data.get('transaction_date'),
                    symbol=transaction_data.get('symbol', ''),
                    name=transaction_data.get('name', ''),
                    transaction_type=transaction_data.get('transaction_type', ''),
                    quantity=transaction_data.get('quantity', 0),
                    price=transaction_data.get('price', 0),
                    amount=transaction_data.get('amount', 0),
                    fee=transaction_data.get('fee', 0)
                )
                session.add(new_transaction)
            
            session.commit()
            logger.info(f"계좌 {account_number} 거래내역 데이터 저장 완료")
            
        except Exception as e:
            session.rollback()
            logger.error(f"거래내역 데이터 저장 실패: {str(e)}")
            raise
        finally:
            session.close()
