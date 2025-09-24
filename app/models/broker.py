"""
브로커 모델
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.utils.database import Base
from datetime import datetime

class Broker(Base):
    """브로커 정보 모델"""
    __tablename__ = 'brokers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    api_type = Column(String(50), nullable=False)
    platform = Column(String(50), nullable=False)
    enabled = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    accounts = relationship("Account", back_populates="broker")
