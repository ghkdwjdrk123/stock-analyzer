"""
토큰 관리 유틸리티 스크립트
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.config import ConfigManager
from app.utils.logger import setup_logging, get_logger
from app.utils.token_manager import TokenManager

def show_token_status():
    """토큰 상태 조회"""
    try:
        # 설정 로드
        config_manager = ConfigManager()
        config = config_manager.config
        
        # 로깅 설정
        setup_logging(config)
        logger = get_logger(__name__)
        
        print("=== 증권사별 토큰 상태 조회 ===")
        
        # 지원하는 증권사 목록
        brokers = ['kis', 'kiwoom']
        
        for broker in brokers:
            print(f"\n--- {broker.upper()} ---")
            try:
                # 증권사별 토큰 관리자 초기화
                token_manager = TokenManager(broker_name=broker)
                tokens = token_manager.list_tokens()
                
                if not tokens:
                    print(f"  저장된 토큰이 없습니다.")
                    continue
                
                for token_name, token_info in tokens.items():
                    if token_info:
                        print(f"  토큰: {token_name}")
                        print(f"    생성 시간: {token_info['created_at']}")
                        print(f"    만료 시간: {token_info['expires_at']}")
                        print(f"    만료 여부: {'만료됨' if token_info['is_expired'] else '유효함'}")
                        print(f"    유효 여부: {'유효함' if token_info['is_valid'] else '무효함'}")
                        print(f"    남은 시간: {token_info['expires_in_hours']:.2f}시간")
                    else:
                        print(f"  토큰: {token_name} - 정보 없음")
                        
            except Exception as e:
                print(f"  {broker} 토큰 조회 실패: {str(e)}")
        
    except Exception as e:
        print(f"토큰 상태 조회 실패: {str(e)}")

def clear_tokens():
    """모든 토큰 삭제"""
    try:
        # 설정 로드
        config_manager = ConfigManager()
        config = config_manager.config
        
        # 로깅 설정
        setup_logging(config)
        logger = get_logger(__name__)
        
        print("=== 모든 증권사 토큰 삭제 ===")
        
        # 지원하는 증권사 목록
        brokers = ['kis', 'kiwoom']
        
        for broker in brokers:
            try:
                # 증권사별 토큰 관리자 초기화
                token_manager = TokenManager(broker_name=broker)
                token_manager.clear_all_tokens()
                print(f"{broker.upper()} 토큰이 삭제되었습니다.")
            except Exception as e:
                print(f"{broker.upper()} 토큰 삭제 실패: {str(e)}")
        
    except Exception as e:
        print(f"토큰 삭제 실패: {str(e)}")

def delete_token(broker_name):
    """특정 브로커 토큰 삭제"""
    try:
        # 설정 로드
        config_manager = ConfigManager()
        config = config_manager.config
        
        # 로깅 설정
        setup_logging(config)
        logger = get_logger(__name__)
        
        # 증권사명을 소문자로 변환
        broker_name = broker_name.lower()
        
        # 토큰 관리자 초기화
        token_manager = TokenManager(broker_name=broker_name)
        
        print(f"=== {broker_name.upper()} 토큰 삭제 ===")
        token_manager.delete_token()
        print(f"{broker_name.upper()}의 토큰이 삭제되었습니다.")
        
    except Exception as e:
        print(f"토큰 삭제 실패: {str(e)}")

def show_help():
    """도움말 표시"""
    print("""
토큰 관리 유틸리티

사용법:
  python manage_tokens.py [명령어]

명령어:
  status     - 토큰 상태 조회
  clear      - 모든 토큰 삭제
  delete     - 특정 브로커 토큰 삭제
  help       - 도움말 표시

예시:
  python manage_tokens.py status
  python manage_tokens.py clear
  python manage_tokens.py delete "kis"
  python manage_tokens.py delete "kiwoom"
""")

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_token_status()
    elif command == "clear":
        clear_tokens()
    elif command == "delete":
        if len(sys.argv) < 3:
            print("브로커 이름을 입력하세요.")
            print("예시: python manage_tokens.py delete \"한국투자증권\"")
            return
        broker_name = sys.argv[2]
        delete_token(broker_name)
    elif command == "help":
        show_help()
    else:
        print(f"알 수 없는 명령어: {command}")
        show_help()

if __name__ == "__main__":
    main()
