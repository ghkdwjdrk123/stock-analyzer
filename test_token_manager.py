"""
토큰 관리 테스트 스크립트
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.config import ConfigManager
from app.utils.database import db_manager, get_database_url
from app.utils.logger import setup_logging, get_logger
from app.utils.token_manager import TokenManager
from app.services.broker_service import BrokerService

def test_token_manager():
    """토큰 관리 테스트"""
    try:
        # 설정 로드
        config_manager = ConfigManager()
        config = config_manager.config
        
        # 로깅 설정
        setup_logging(config)
        logger = get_logger(__name__)
        logger.info("토큰 관리 테스트를 시작합니다.")
        
        # 데이터베이스 초기화
        database_config = config.get('database', {})
        database_url = get_database_url(database_config)
        db_manager.init_database(database_url)
        logger.info("데이터베이스 초기화 완료")
        
        # 토큰 관리자 테스트 (증권사별)
        token_manager = TokenManager(broker_name="kis")
        
        # 1. 토큰 상태 확인
        logger.info("=== KIS 토큰 상태 확인 ===")
        token_info = token_manager.get_token_expiry_info()
        if token_info:
            logger.info(f"토큰 생성 시간: {token_info['created_at']}")
            logger.info(f"토큰 만료 시간: {token_info['expires_at']}")
            logger.info(f"토큰 만료 여부: {token_info['is_expired']}")
            logger.info(f"토큰 유효 여부: {token_info['is_valid']}")
            logger.info(f"남은 시간: {token_info['expires_in_hours']:.2f}시간")
        else:
            logger.info("저장된 토큰이 없습니다.")
        
        # 2. 브로커 서비스 초기화 및 연결
        logger.info("=== 브로커 서비스 테스트 ===")
        broker_service = BrokerService(config)
        kis_broker = broker_service.get_broker("한국투자증권")
        
        if kis_broker:
            try:
                # API 연결 (토큰 자동 관리)
                logger.info("한국투자증권 API 연결을 시도합니다.")
                kis_broker.connect()
                logger.info("한국투자증권 API 연결 성공!")
                
                # 토큰 상태 재확인
                logger.info("=== 연결 후 토큰 상태 ===")
                token_info = token_manager.get_token_expiry_info()
                if token_info:
                    logger.info(f"토큰 생성 시간: {token_info['created_at']}")
                    logger.info(f"토큰 만료 시간: {token_info['expires_at']}")
                    logger.info(f"토큰 만료 여부: {token_info['is_expired']}")
                    logger.info(f"토큰 유효 여부: {token_info['is_valid']}")
                    logger.info(f"남은 시간: {token_info['expires_in_hours']:.2f}시간")
                
                # 간단한 API 호출 테스트
                logger.info("=== API 호출 테스트 ===")
                accounts = kis_broker.get_accounts()
                logger.info(f"조회된 계좌 수: {len(accounts)}")
                
                # 연결 해제
                kis_broker.disconnect()
                logger.info("한국투자증권 API 연결이 해제되었습니다.")
                
            except Exception as e:
                logger.error(f"브로커 테스트 실패: {str(e)}")
        
        # 3. 토큰 파일 확인
        logger.info("=== 토큰 파일 확인 ===")
        token_file_path = "./token/kis/tokens.json"
        if os.path.exists(token_file_path):
            logger.info(f"KIS 토큰 파일이 생성되었습니다: {token_file_path}")
            with open(token_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"토큰 파일 내용 (일부): {content[:200]}...")
        else:
            logger.warning("KIS 토큰 파일이 생성되지 않았습니다.")
        
        logger.info("토큰 관리 테스트가 완료되었습니다!")
        return True
        
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_token_manager()
    if success:
        print("\nSuccess: 토큰 관리 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\nError: 토큰 관리 테스트에 실패했습니다.")
        sys.exit(1)
