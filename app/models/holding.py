"""
보유종목 모델
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime

class Holding(Base):
    """보유종목 모델"""
    __tablename__ = 'holdings'

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=0)
    average_price = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    evaluation_amount = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    profit_loss_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # API 데이터 최종 업데이트 시간

    # 계좌별 종목 고유 제약조건 (계좌당 종목은 하나의 레코드만)
    __table_args__ = (
        UniqueConstraint('account_id', 'symbol', name='uq_account_symbol'),
    )

    # 관계
    account = relationship("Account", back_populates="holdings")
