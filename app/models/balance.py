"""
잔고 관련 모델
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime

class DailyBalance(Base):
    """일일 잔고 모델"""
    __tablename__ = 'daily_balances'

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    balance_date = Column(Date, nullable=False, index=True)
    cash_balance = Column(Float, default=0.0)
    stock_balance = Column(Float, default=0.0)
    total_balance = Column(Float, default=0.0)
    evaluation_amount = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    profit_loss_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 계좌별 날짜 고유 제약조건 (하루에 하나의 레코드만)
    __table_args__ = (
        UniqueConstraint('account_id', 'balance_date', name='uq_account_balance_date'),
    )

    # 관계
    account = relationship("Account", back_populates="daily_balances")
