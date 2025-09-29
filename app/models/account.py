"""
계좌 모델
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime

class Account(Base):
    """계좌 정보 모델"""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, index=True)
    broker_id = Column(Integer, ForeignKey('brokers.id'), nullable=False)
    account_number = Column(String(50), nullable=False, index=True)
    account_name = Column(String(100))
    account_type = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    broker = relationship("Broker", back_populates="accounts")
    daily_balances = relationship("DailyBalance", back_populates="account")
    holdings = relationship("Holding", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")
    monthly_summaries = relationship("MonthlySummary", back_populates="account")
    stock_performances = relationship("StockPerformance", back_populates="account")
    portfolio_analyses = relationship("PortfolioAnalysis", back_populates="account")
    trading_patterns = relationship("TradingPattern", back_populates="account")
    risk_metrics = relationship("RiskMetrics", back_populates="account")
