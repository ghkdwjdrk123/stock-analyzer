"""
보유종목 모델
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date
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
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    account = relationship("Account", back_populates="holdings")
