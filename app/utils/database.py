"""
데이터베이스 관리 클래스
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
import os
from typing import Optional

Base = declarative_base()

class DatabaseManager:
    """데이터베이스 관리 클래스"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.database_url = None
    
    def init_database(self, database_url: str):
        """데이터베이스 초기화"""
        try:
            self.database_url = database_url
            
            # SQLite의 경우 추가 설정
            if database_url.startswith('sqlite'):
                self.engine = create_engine(
                    database_url,
                    poolclass=StaticPool,
                    connect_args={'check_same_thread': False}
                )
            else:
                self.engine = create_engine(database_url)
            
            # 세션 팩토리 생성
            self.SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine
            )
            
            # 테이블 생성
            Base.metadata.create_all(bind=self.engine)
            
            return True
            
        except Exception as e:
            raise Exception(f"데이터베이스 초기화 실패: {str(e)}")
    
    def get_session(self):
        """데이터베이스 세션 반환"""
        if not self.SessionLocal:
            raise Exception("데이터베이스가 초기화되지 않았습니다.")
        return self.SessionLocal()
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()

def get_database_url(config: dict) -> str:
    """설정에서 데이터베이스 URL 생성"""
    db_type = config.get('type', 'sqlite')
    
    if db_type == 'sqlite':
        db_path = config.get('path', './data/stock_analyzer.db')
        # 디렉토리 생성
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f"sqlite:///{db_path}"
    
    elif db_type == 'postgresql':
        host = config.get('host', 'localhost')
        port = config.get('port', 5432)
        name = config.get('name', 'stock_analyzer')
        username = config.get('username', 'postgres')
        password = config.get('password', '')
        return f"postgresql://{username}:{password}@{host}:{port}/{name}"
    
    else:
        raise ValueError(f"지원하지 않는 데이터베이스 타입: {db_type}")
