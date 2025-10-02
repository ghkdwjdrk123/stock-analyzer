"""
키움증권 영웅문 API 연동 클래스
32비트 서브프로세스 방식
"""
import subprocess
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pathlib import Path
from app.brokers.base_broker import BaseBroker
from app.utils.exceptions import BrokerError, AuthenticationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class KiwoomBroker(BaseBroker):
    """키움증권 브로커 클래스 (32비트 서브프로세스 방식)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.credentials = config.get('credentials', {})
        self.api_settings = config.get('api_settings', {})

        # 환경변수에서 계좌 정보 로드
        from dotenv import load_dotenv
        load_dotenv('env')

        # 32비트 Python 경로 (환경변수 또는 기본값)
        self.python32_path = os.getenv('PYTHON32_PATH', 'python')

        # Worker 스크립트 경로
        project_root = Path(__file__).parent.parent.parent
        self.worker_script = project_root / 'workers' / 'kiwoom_worker_32.py'

        # 연결 상태 캐싱
        self._accounts_cache = None

    def connect(self) -> bool:
        """브로커 연결 (실제로는 서브프로세스 실행 가능 여부만 확인)"""
        try:
            logger.info(f"{self.name} API 준비 완료 (32비트 서브프로세스 방식)")
            self.connected = True
            return True

        except Exception as e:
            logger.error(f"{self.name} API 준비 실패: {str(e)}")
            self.connected = False
            raise BrokerError(f"API 준비 실패: {str(e)}")

    def disconnect(self) -> bool:
        """브로커 연결 해제"""
        try:
            self.connected = False
            self._accounts_cache = None
            logger.info(f"{self.name} API 연결 해제")
            return True

        except Exception as e:
            logger.error(f"{self.name} API 연결 해제 실패: {str(e)}")
            return False

    def _run_worker(self, command: str, *args) -> Dict[str, Any]:
        """32비트 Worker 프로세스 실행"""
        try:
            # 명령어 구성
            cmd = [self.python32_path, str(self.worker_script), command] + list(args)

            logger.debug(f"Worker 실행: {' '.join(cmd)}")

            # 서브프로세스 실행
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )

            # 결과 파싱
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "알 수 없는 오류"
                logger.error(f"Worker 실행 실패: {error_msg}")
                raise BrokerError(f"Worker 실행 실패: {error_msg}")

            # JSON 파싱
            try:
                response = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 실패: {result.stdout}")
                raise BrokerError(f"응답 파싱 실패: {str(e)}")

            # 성공 여부 확인
            if not response.get('success', False):
                error = response.get('error', '알 수 없는 오류')
                raise BrokerError(f"Worker 오류: {error}")

            return response

        except subprocess.TimeoutExpired:
            logger.error("Worker 타임아웃")
            raise BrokerError("Worker 실행 타임아웃 (60초)")
        except Exception as e:
            logger.error(f"Worker 실행 중 오류: {str(e)}")
            raise BrokerError(f"Worker 실행 오류: {str(e)}")

    def get_accounts(self) -> List[Dict[str, Any]]:
        """계좌 목록 조회"""
        try:
            # 캐시 확인
            if self._accounts_cache is not None:
                logger.debug("캐시된 계좌 목록 반환")
                return self._accounts_cache

            logger.info("계좌 목록 조회 중...")

            # Worker 실행
            response = self._run_worker('get_accounts')

            accounts = response.get('data', [])

            # 캐시 저장
            self._accounts_cache = accounts

            logger.info(f"계좌 {len(accounts)}개 조회 완료")
            return accounts

        except Exception as e:
            logger.error(f"계좌 목록 조회 실패: {str(e)}")
            raise BrokerError(f"계좌 목록 조회 실패: {str(e)}")

    def get_balance(self, account_number: str) -> Dict[str, Any]:
        """계좌 잔고 조회"""
        try:
            logger.info(f"계좌 {account_number} 잔고 조회 중...")

            # Worker 실행
            response = self._run_worker('get_balance', account_number)

            balance_info = response.get('data', {})

            logger.info(f"계좌 {account_number} 잔고 조회 완료")
            return balance_info

        except Exception as e:
            logger.error(f"계좌 {account_number} 잔고 조회 실패: {str(e)}")
            raise BrokerError(f"잔고 조회 실패: {str(e)}")

    def get_holdings(self, account_number: str) -> List[Dict[str, Any]]:
        """보유종목 조회"""
        try:
            logger.info(f"계좌 {account_number} 보유종목 조회 중...")

            # Worker 실행
            response = self._run_worker('get_holdings', account_number)

            holdings = response.get('data', [])

            logger.info(f"계좌 {account_number} 보유종목 {len(holdings)}개 조회 완료")
            return holdings

        except Exception as e:
            logger.error(f"계좌 {account_number} 보유종목 조회 실패: {str(e)}")
            raise BrokerError(f"보유종목 조회 실패: {str(e)}")

    def get_transactions(self, account_number: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """거래내역 조회 (추후 구현)"""
        logger.warning("거래내역 조회는 아직 구현되지 않았습니다.")
        return []
