"""
키움증권 브로커 테스트 스크립트
"""
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from app.brokers.kiwoom_broker import KiwoomBroker
from app.utils.config import ConfigManager
from app.utils.logger import get_logger

logger = get_logger(__name__)


def test_kiwoom_broker():
    """키움 브로커 기본 테스트"""

    print("=" * 80)
    print("키움증권 브로커 테스트")
    print("=" * 80)
    print()

    try:
        # 설정 로드
        print("1. 설정 파일 로드 중...")
        config_manager = ConfigManager()
        config = config_manager.config

        # 키움 브로커 설정 찾기
        kiwoom_config = None
        for broker_config in config.get('brokers', []):
            if broker_config.get('api_type') == 'kiwoom':
                kiwoom_config = broker_config
                break

        if not kiwoom_config:
            print("[ERROR] config.json에 키움 브로커 설정이 없습니다.")
            return False

        print(f"[OK] 브로커 설정 로드 완료: {kiwoom_config.get('name')}")
        print()

        # Qt 애플리케이션 시작 (키움 API 필수)
        print("2. Qt 애플리케이션 초기화 중...")
        app = QApplication(sys.argv)
        print("[OK] Qt 애플리케이션 초기화 완료")
        print()

        # 브로커 초기화
        print("3. 키움 브로커 초기화 중...")
        broker = KiwoomBroker(kiwoom_config)
        print("[OK] 키움 브로커 초기화 완료")
        print()

        # 연결 테스트
        print("4. 키움 API 연결 중...")
        print("[WARN] 로그인 창이 표시됩니다. 로그인을 진행해주세요.")
        broker.connect()
        print("[OK] 키움 API 연결 완료")
        print()

        # 계좌 목록 조회
        print("5. 계좌 목록 조회 중...")
        accounts = broker.get_accounts()
        print(f"[OK] 계좌 {len(accounts)}개 조회 완료")

        for idx, account in enumerate(accounts, 1):
            print(f"   [{idx}] {account['account_number']} - {account['account_name']}")
        print()

        if len(accounts) > 0:
            # 첫 번째 계좌로 테스트
            test_account = accounts[0]['account_number']

            # 잔고 조회 테스트
            print(f"6. 계좌 잔고 조회 중... (계좌: {test_account})")
            balance = broker.get_balance(test_account)

            print("[OK] 잔고 조회 완료")
            print(f"   - 현금잔고: {balance['cash_balance']:,.0f}원")
            print(f"   - 주식잔고: {balance['stock_balance']:,.0f}원")
            print(f"   - 총자산: {balance['total_balance']:,.0f}원")
            print(f"   - 평가손익: {balance['profit_loss']:,.0f}원 ({balance['profit_loss_rate']:.2f}%)")
            print()

            # 보유종목 조회 테스트
            print(f"7. 보유종목 조회 중... (계좌: {test_account})")
            holdings = broker.get_holdings(test_account)

            print(f"[OK] 보유종목 {len(holdings)}개 조회 완료")

            if len(holdings) > 0:
                print("\n   보유종목 목록:")
                for idx, holding in enumerate(holdings, 1):
                    print(f"   [{idx}] {holding['name']} ({holding['symbol']})")
                    print(f"       수량: {holding['quantity']:,}주")
                    print(f"       평균단가: {holding['average_price']:,.0f}원")
                    print(f"       현재가: {holding['current_price']:,.0f}원")
                    print(f"       평가금액: {holding['evaluation_amount']:,.0f}원")
                    print(f"       손익: {holding['profit_loss']:,.0f}원 ({holding['profit_loss_rate']:.2f}%)")
                    print()
            else:
                print("   보유종목이 없습니다.")

        # 연결 해제
        print("8. 키움 API 연결 해제 중...")
        broker.disconnect()
        print("[OK] 연결 해제 완료")
        print()

        print("=" * 80)
        print("[OK] 모든 테스트 완료!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {str(e)}")
        logger.error(f"키움 브로커 테스트 실패: {str(e)}", exc_info=True)
        return False


def test_without_login():
    """로그인 없이 초기화만 테스트"""

    print("=" * 80)
    print("키움증권 브로커 초기화 테스트 (로그인 제외)")
    print("=" * 80)
    print()

    try:
        # 설정 로드
        print("1. 설정 파일 로드 중...")
        config_manager = ConfigManager()
        config = config_manager.config

        kiwoom_config = None
        for broker_config in config.get('brokers', []):
            if broker_config.get('api_type') == 'kiwoom':
                kiwoom_config = broker_config
                break

        if not kiwoom_config:
            print("[ERROR] config.json에 키움 브로커 설정이 없습니다.")
            return False

        print("[OK] 브로커 설정 로드 완료")
        print()

        # Qt 애플리케이션
        print("2. Qt 애플리케이션 초기화 중...")
        app = QApplication(sys.argv)
        print("[OK] Qt 애플리케이션 초기화 완료")
        print()

        # 브로커 초기화만
        print("3. 키움 브로커 초기화 중...")
        broker = KiwoomBroker(kiwoom_config)
        print("[OK] 키움 브로커 초기화 완료")
        print()

        # 브로커 정보 출력
        info = broker.get_broker_info()
        print("브로커 정보:")
        print(f"  - 이름: {info['name']}")
        print(f"  - API 타입: {info['api_type']}")
        print(f"  - 활성화: {info['enabled']}")
        print(f"  - 연결 상태: {info['connected']}")
        print()

        print("=" * 80)
        print("[OK] 초기화 테스트 완료!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n[ERROR] 테스트 실패: {str(e)}")
        logger.error(f"키움 브로커 초기화 테스트 실패: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    print("\n키움증권 브로커 테스트 스크립트")
    print("=" * 80)
    print()
    print("테스트 옵션:")
    print("  1. 전체 테스트 (로그인 포함)")
    print("  2. 초기화 테스트만 (로그인 제외)")
    print()

    choice = input("선택 (1 또는 2): ").strip()
    print()

    if choice == "1":
        success = test_kiwoom_broker()
    elif choice == "2":
        success = test_without_login()
    else:
        print("[ERROR] 잘못된 선택입니다.")
        sys.exit(1)

    sys.exit(0 if success else 1)
