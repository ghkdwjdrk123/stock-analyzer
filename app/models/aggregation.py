"""
분석용 집계 데이터 모델
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime

class MonthlySummary(Base):
    """월별 요약 데이터 모델"""
    __tablename__ = 'monthly_summaries'
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    
    # 월별 집계 데이터
    total_balance = Column(Float, default=0.0)
    total_investment = Column(Float, default=0.0)
    total_profit_loss = Column(Float, default=0.0)
    profit_loss_rate = Column(Float, default=0.0)
    
    # 거래 통계
    total_transactions = Column(Integer, default=0)
    total_buy_amount = Column(Float, default=0.0)
    total_sell_amount = Column(Float, default=0.0)
    total_fees = Column(Float, default=0.0)
    
    # 보유종목 통계
    total_holdings = Column(Integer, default=0)
    avg_holding_period = Column(Float, default=0.0)
    
    # 성과 지표
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    volatility = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    account = relationship("Account", back_populates="monthly_summaries")

class StockPerformance(Base):
    """종목별 성과 분석 모델"""
    __tablename__ = 'stock_performances'
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    symbol = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    
    # 성과 지표
    total_investment = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)
    total_profit_loss = Column(Float, default=0.0)
    profit_loss_rate = Column(Float, default=0.0)
    
    # 거래 통계
    total_buy_quantity = Column(Integer, default=0)
    total_sell_quantity = Column(Integer, default=0)
    avg_buy_price = Column(Float, default=0.0)
    avg_sell_price = Column(Float, default=0.0)
    
    # 보유 기간
    first_buy_date = Column(Date)
    last_sell_date = Column(Date)
    holding_days = Column(Integer, default=0)
    
    # 수익률 분석
    max_profit_rate = Column(Float, default=0.0)
    max_loss_rate = Column(Float, default=0.0)
    avg_daily_return = Column(Float, default=0.0)
    
    # 위험 지표
    volatility = Column(Float, default=0.0)
    beta = Column(Float, default=0.0)
    
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    account = relationship("Account", back_populates="stock_performances")

class PortfolioAnalysis(Base):
    """포트폴리오 분석 모델"""
    __tablename__ = 'portfolio_analyses'
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    analysis_date = Column(Date, nullable=False)
    
    # 포트폴리오 구성
    total_assets = Column(Float, default=0.0)
    cash_ratio = Column(Float, default=0.0)
    stock_ratio = Column(Float, default=0.0)
    diversification_score = Column(Float, default=0.0)
    
    # 성과 지표
    total_return = Column(Float, default=0.0)
    annualized_return = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    sortino_ratio = Column(Float, default=0.0)
    
    # 위험 지표
    volatility = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    var_95 = Column(Float, default=0.0)  # 95% VaR
    var_99 = Column(Float, default=0.0)  # 99% VaR
    
    # 거래 패턴
    turnover_rate = Column(Float, default=0.0)
    avg_holding_period = Column(Float, default=0.0)
    trading_frequency = Column(Float, default=0.0)
    
    # 섹터 분석 (JSON 형태로 저장)
    sector_allocation = Column(Text)  # JSON 문자열
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    account = relationship("Account", back_populates="portfolio_analyses")

class TradingPattern(Base):
    """거래 패턴 분석 모델"""
    __tablename__ = 'trading_patterns'
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    pattern_type = Column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly'
    pattern_date = Column(Date, nullable=False)
    
    # 거래 통계
    total_transactions = Column(Integer, default=0)
    buy_transactions = Column(Integer, default=0)
    sell_transactions = Column(Integer, default=0)
    
    # 거래 금액
    total_buy_amount = Column(Float, default=0.0)
    total_sell_amount = Column(Float, default=0.0)
    net_trading_amount = Column(Float, default=0.0)
    
    # 수수료 분석
    total_fees = Column(Float, default=0.0)
    fee_ratio = Column(Float, default=0.0)
    
    # 시간대별 거래 패턴
    morning_trades = Column(Integer, default=0)
    afternoon_trades = Column(Integer, default=0)
    evening_trades = Column(Integer, default=0)
    
    # 거래 규모 분석
    large_trades = Column(Integer, default=0)  # 100만원 이상
    medium_trades = Column(Integer, default=0)  # 10만원~100만원
    small_trades = Column(Integer, default=0)   # 10만원 미만
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    account = relationship("Account", back_populates="trading_patterns")

class RiskMetrics(Base):
    """위험 지표 모델"""
    __tablename__ = 'risk_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    calculation_date = Column(Date, nullable=False)
    
    # 변동성 지표
    daily_volatility = Column(Float, default=0.0)
    monthly_volatility = Column(Float, default=0.0)
    annual_volatility = Column(Float, default=0.0)
    
    # 하방 위험 지표
    downside_deviation = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    max_drawdown_duration = Column(Integer, default=0)  # 일수
    
    # VaR (Value at Risk)
    var_1d_95 = Column(Float, default=0.0)
    var_1d_99 = Column(Float, default=0.0)
    var_1m_95 = Column(Float, default=0.0)
    var_1m_99 = Column(Float, default=0.0)
    
    # 기타 위험 지표
    sharpe_ratio = Column(Float, default=0.0)
    sortino_ratio = Column(Float, default=0.0)
    calmar_ratio = Column(Float, default=0.0)
    
    # 상관관계 분석
    market_correlation = Column(Float, default=0.0)
    beta = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    account = relationship("Account", back_populates="risk_metrics")
