"""
분석 데이터 생성 및 관리 서비스
"""
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from app.models.account import Account
from app.models.balance import DailyBalance
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.models.aggregation import (
    MonthlySummary, StockPerformance, PortfolioAnalysis, 
    TradingPattern, RiskMetrics
)
from app.utils.database import db_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AnalysisService:
    """분석 데이터 생성 서비스"""
    
    def __init__(self):
        self.session = None
    
    def _get_session(self) -> Session:
        """데이터베이스 세션 가져오기"""
        if not self.session:
            self.session = db_manager.get_session()
        return self.session
    
    def generate_monthly_summary(self, account_id: int, year: int, month: int) -> MonthlySummary:
        """월별 요약 데이터 생성"""
        try:
            session = self._get_session()
            
            # 해당 월의 시작일과 종료일
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            # 일일 잔고 데이터 조회
            daily_balances = session.query(DailyBalance).filter(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date >= start_date,
                    DailyBalance.balance_date <= end_date
                )
            ).order_by(DailyBalance.balance_date).all()
            
            if not daily_balances:
                logger.warning(f"월별 요약 데이터 없음: account_id={account_id}, {year}-{month}")
                return None
            
            # 거래 데이터 조회
            transactions = session.query(Transaction).filter(
                and_(
                    Transaction.account_id == account_id,
                    Transaction.transaction_date >= start_date,
                    Transaction.transaction_date <= end_date
                )
            ).all()
            
            # 보유종목 데이터 조회
            holdings = session.query(Holding).filter(
                and_(
                    Holding.account_id == account_id,
                    Holding.last_updated >= start_date
                )
            ).all()
            
            # 집계 계산
            monthly_data = self._calculate_monthly_metrics(
                daily_balances, transactions, holdings, start_date, end_date
            )
            
            # 기존 데이터 업데이트 또는 새로 생성
            existing = session.query(MonthlySummary).filter(
                and_(
                    MonthlySummary.account_id == account_id,
                    MonthlySummary.year == year,
                    MonthlySummary.month == month
                )
            ).first()
            
            if existing:
                for key, value in monthly_data.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"월별 요약 데이터 업데이트: account_id={account_id}, {year}-{month}")
                return existing
            else:
                monthly_summary = MonthlySummary(
                    account_id=account_id,
                    year=year,
                    month=month,
                    **monthly_data
                )
                session.add(monthly_summary)
                session.commit()
                logger.info(f"월별 요약 데이터 생성: account_id={account_id}, {year}-{month}")
                return monthly_summary
                
        except Exception as e:
            logger.error(f"월별 요약 데이터 생성 실패: {str(e)}")
            raise
    
    def generate_stock_performance(self, account_id: int, symbol: str) -> StockPerformance:
        """종목별 성과 분석 데이터 생성"""
        try:
            session = self._get_session()
            
            # 해당 종목의 거래 내역 조회
            transactions = session.query(Transaction).filter(
                and_(
                    Transaction.account_id == account_id,
                    Transaction.symbol == symbol
                )
            ).order_by(Transaction.transaction_date).all()
            
            if not transactions:
                logger.warning(f"종목 거래 내역 없음: account_id={account_id}, symbol={symbol}")
                return None
            
            # 보유종목 데이터 조회
            holding = session.query(Holding).filter(
                and_(
                    Holding.account_id == account_id,
                    Holding.symbol == symbol
                )
            ).first()
            
            # 성과 계산
            performance_data = self._calculate_stock_performance(transactions, holding)
            
            # 기존 데이터 업데이트 또는 새로 생성
            existing = session.query(StockPerformance).filter(
                and_(
                    StockPerformance.account_id == account_id,
                    StockPerformance.symbol == symbol
                )
            ).first()
            
            if existing:
                for key, value in performance_data.items():
                    setattr(existing, key, value)
                existing.last_updated = datetime.utcnow()
                session.commit()
                logger.info(f"종목 성과 데이터 업데이트: account_id={account_id}, symbol={symbol}")
                return existing
            else:
                stock_performance = StockPerformance(
                    account_id=account_id,
                    symbol=symbol,
                    name=transactions[0].name if transactions else "",
                    **performance_data
                )
                session.add(stock_performance)
                session.commit()
                logger.info(f"종목 성과 데이터 생성: account_id={account_id}, symbol={symbol}")
                return stock_performance
                
        except Exception as e:
            logger.error(f"종목 성과 데이터 생성 실패: {str(e)}")
            raise
    
    def generate_portfolio_analysis(self, account_id: int, analysis_date: date = None) -> PortfolioAnalysis:
        """포트폴리오 분석 데이터 생성"""
        try:
            session = self._get_session()
            
            if not analysis_date:
                analysis_date = date.today()
            
            # 해당 날짜의 잔고 데이터 조회
            balance = session.query(DailyBalance).filter(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date == analysis_date
                )
            ).first()
            
            if not balance:
                logger.warning(f"포트폴리오 분석 데이터 없음: account_id={account_id}, date={analysis_date}")
                return None
            
            # 보유종목 데이터 조회
            holdings = session.query(Holding).filter(
                and_(
                    Holding.account_id == account_id,
                    Holding.last_updated >= analysis_date - timedelta(days=7)  # 최근 7일 내 업데이트
                )
            ).all()
            
            # 과거 1년간의 일일 잔고 데이터 조회 (성과 분석용)
            start_date = analysis_date - timedelta(days=365)
            historical_balances = session.query(DailyBalance).filter(
                and_(
                    DailyBalance.account_id == account_id,
                    DailyBalance.balance_date >= start_date,
                    DailyBalance.balance_date <= analysis_date
                )
            ).order_by(DailyBalance.balance_date).all()
            
            # 분석 데이터 계산
            analysis_data = self._calculate_portfolio_metrics(
                balance, holdings, historical_balances, analysis_date
            )
            
            # 기존 데이터 업데이트 또는 새로 생성
            existing = session.query(PortfolioAnalysis).filter(
                and_(
                    PortfolioAnalysis.account_id == account_id,
                    PortfolioAnalysis.analysis_date == analysis_date
                )
            ).first()
            
            if existing:
                for key, value in analysis_data.items():
                    setattr(existing, key, value)
                session.commit()
                logger.info(f"포트폴리오 분석 데이터 업데이트: account_id={account_id}, date={analysis_date}")
                return existing
            else:
                portfolio_analysis = PortfolioAnalysis(
                    account_id=account_id,
                    analysis_date=analysis_date,
                    **analysis_data
                )
                session.add(portfolio_analysis)
                session.commit()
                logger.info(f"포트폴리오 분석 데이터 생성: account_id={account_id}, date={analysis_date}")
                return portfolio_analysis
                
        except Exception as e:
            logger.error(f"포트폴리오 분석 데이터 생성 실패: {str(e)}")
            raise
    
    def _calculate_monthly_metrics(self, daily_balances: List[DailyBalance], 
                                 transactions: List[Transaction], 
                                 holdings: List[Holding],
                                 start_date: date, end_date: date) -> Dict[str, Any]:
        """월별 지표 계산"""
        try:
            # 기본 데이터
            first_balance = daily_balances[0] if daily_balances else None
            last_balance = daily_balances[-1] if daily_balances else None
            
            # 총 자산 및 수익률
            total_balance = last_balance.total_balance if last_balance else 0
            total_investment = first_balance.total_balance if first_balance else 0
            total_profit_loss = last_balance.profit_loss if last_balance else 0
            profit_loss_rate = last_balance.profit_loss_rate if last_balance else 0
            
            # 거래 통계
            total_transactions = len(transactions)
            buy_transactions = len([t for t in transactions if t.transaction_type == 'BUY'])
            sell_transactions = len([t for t in transactions if t.transaction_type == 'SELL'])
            
            total_buy_amount = sum(t.amount for t in transactions if t.transaction_type == 'BUY')
            total_sell_amount = sum(t.amount for t in transactions if t.transaction_type == 'SELL')
            total_fees = sum(t.fee for t in transactions)
            
            # 보유종목 통계
            total_holdings = len(holdings)
            
            # 평균 보유 기간 계산 (간단한 버전)
            if holdings:
                holding_days = [(end_date - h.last_updated.date()).days for h in holdings]
                avg_holding_period = np.mean(holding_days) if holding_days else 0
            else:
                avg_holding_period = 0
            
            # 성과 지표 (간단한 버전)
            sharpe_ratio = 0.0  # 추후 구현
            max_drawdown = 0.0  # 추후 구현
            volatility = 0.0    # 추후 구현
            
            return {
                'total_balance': total_balance,
                'total_investment': total_investment,
                'total_profit_loss': total_profit_loss,
                'profit_loss_rate': profit_loss_rate,
                'total_transactions': total_transactions,
                'total_buy_amount': total_buy_amount,
                'total_sell_amount': total_sell_amount,
                'total_fees': total_fees,
                'total_holdings': total_holdings,
                'avg_holding_period': avg_holding_period,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'volatility': volatility
            }
            
        except Exception as e:
            logger.error(f"월별 지표 계산 실패: {str(e)}")
            raise
    
    def _calculate_stock_performance(self, transactions: List[Transaction], 
                                   holding: Optional[Holding]) -> Dict[str, Any]:
        """종목별 성과 지표 계산"""
        try:
            # 기본 통계
            buy_transactions = [t for t in transactions if t.transaction_type == 'BUY']
            sell_transactions = [t for t in transactions if t.transaction_type == 'SELL']
            
            total_buy_quantity = sum(t.quantity for t in buy_transactions)
            total_sell_quantity = sum(t.quantity for t in sell_transactions)
            total_investment = sum(t.amount for t in buy_transactions)
            
            # 평균 단가
            avg_buy_price = total_investment / total_buy_quantity if total_buy_quantity > 0 else 0
            avg_sell_price = sum(t.amount for t in sell_transactions) / total_sell_quantity if total_sell_quantity > 0 else 0
            
            # 현재 보유량
            current_quantity = total_buy_quantity - total_sell_quantity
            
            # 현재 가치 및 수익
            if holding:
                current_value = holding.evaluation_amount
                current_price = holding.current_price
            else:
                current_value = current_quantity * avg_buy_price  # 추정치
                current_price = avg_buy_price
            
            total_profit_loss = current_value - (current_quantity * avg_buy_price)
            profit_loss_rate = (total_profit_loss / (current_quantity * avg_buy_price)) * 100 if current_quantity * avg_buy_price > 0 else 0
            
            # 거래 날짜
            first_buy_date = min(t.transaction_date for t in buy_transactions) if buy_transactions else None
            last_sell_date = max(t.transaction_date for t in sell_transactions) if sell_transactions else None
            
            # 보유 기간
            holding_days = 0
            if first_buy_date:
                end_date = last_sell_date if last_sell_date else date.today()
                holding_days = (end_date - first_buy_date).days
            
            return {
                'total_investment': total_investment,
                'current_value': current_value,
                'total_profit_loss': total_profit_loss,
                'profit_loss_rate': profit_loss_rate,
                'total_buy_quantity': total_buy_quantity,
                'total_sell_quantity': total_sell_quantity,
                'avg_buy_price': avg_buy_price,
                'avg_sell_price': avg_sell_price,
                'first_buy_date': first_buy_date,
                'last_sell_date': last_sell_date,
                'holding_days': holding_days,
                'max_profit_rate': profit_loss_rate,  # 간단한 버전
                'max_loss_rate': min(0, profit_loss_rate),  # 간단한 버전
                'avg_daily_return': profit_loss_rate / max(1, holding_days) if holding_days > 0 else 0,
                'volatility': 0.0,  # 추후 구현
                'beta': 0.0  # 추후 구현
            }
            
        except Exception as e:
            logger.error(f"종목 성과 지표 계산 실패: {str(e)}")
            raise
    
    def _calculate_portfolio_metrics(self, balance: DailyBalance, 
                                   holdings: List[Holding], 
                                   historical_balances: List[DailyBalance],
                                   analysis_date: date) -> Dict[str, Any]:
        """포트폴리오 지표 계산"""
        try:
            # 포트폴리오 구성
            total_assets = balance.total_balance
            cash_ratio = (balance.cash_balance / total_assets) * 100 if total_assets > 0 else 0
            stock_ratio = (balance.stock_balance / total_assets) * 100 if total_assets > 0 else 0
            
            # 다각화 점수 (보유종목 수 기반)
            diversification_score = min(100, len(holdings) * 10) if holdings else 0
            
            # 성과 지표
            total_return = balance.profit_loss_rate
            
            # 연간 수익률 (간단한 버전)
            if len(historical_balances) >= 2:
                start_balance = historical_balances[0].total_balance
                end_balance = historical_balances[-1].total_balance
                days = (historical_balances[-1].balance_date - historical_balances[0].balance_date).days
                annualized_return = ((end_balance / start_balance) ** (365 / days) - 1) * 100 if days > 0 and start_balance > 0 else 0
            else:
                annualized_return = total_return
            
            # 거래 패턴 (간단한 버전)
            turnover_rate = 0.0  # 추후 구현
            avg_holding_period = 0.0  # 추후 구현
            trading_frequency = 0.0  # 추후 구현
            
            return {
                'total_assets': total_assets,
                'cash_ratio': cash_ratio,
                'stock_ratio': stock_ratio,
                'diversification_score': diversification_score,
                'total_return': total_return,
                'annualized_return': annualized_return,
                'sharpe_ratio': 0.0,  # 추후 구현
                'sortino_ratio': 0.0,  # 추후 구현
                'volatility': 0.0,  # 추후 구현
                'max_drawdown': 0.0,  # 추후 구현
                'var_95': 0.0,  # 추후 구현
                'var_99': 0.0,  # 추후 구현
                'turnover_rate': turnover_rate,
                'avg_holding_period': avg_holding_period,
                'trading_frequency': trading_frequency,
                'sector_allocation': '{}'  # 추후 구현
            }
            
        except Exception as e:
            logger.error(f"포트폴리오 지표 계산 실패: {str(e)}")
            raise
    
    def close_session(self):
        """세션 종료"""
        if self.session:
            self.session.close()
            self.session = None
