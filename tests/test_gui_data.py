"""
GUI 데이터 조회 테스트 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.utils.data_service import DataService

def test_data_service():
    """DataService 테스트"""
    print("=== GUI DataService 테스트 ===")
    
    try:
        data_service = DataService()
        
        # 1. 계좌 목록 조회
        print("\n1. 계좌 목록 조회")
        accounts = data_service.get_accounts()
        print(f"조회된 계좌 수: {len(accounts)}")
        for acc in accounts:
            print(f"  - ID: {acc['id']}, 증권사: {acc['broker_name']}, 계좌번호: {acc['account_number']}")
        
        if accounts:
            # 첫 번째 계좌로 테스트
            test_account_id = accounts[0]['id']
            print(f"\n테스트 계좌 ID: {test_account_id}")
            
            # 2. 최신 잔고 조회
            print("\n2. 최신 잔고 조회")
            latest_balance = data_service.get_latest_balance(test_account_id)
            if latest_balance:
                print(f"  - 총자산: {latest_balance['total_balance']:,.0f}원")
                print(f"  - 현금잔고: {latest_balance['cash_balance']:,.0f}원")
                print(f"  - 주식잔고: {latest_balance['stock_balance']:,.0f}원")
                print(f"  - 수익률: {latest_balance['profit_loss_rate']:.2f}%")
            else:
                print("  - 잔고 데이터 없음")
            
            # 3. 보유종목 조회
            print("\n3. 보유종목 조회")
            holdings = data_service.get_holdings(test_account_id)
            print(f"조회된 보유종목 수: {len(holdings)}")
            for holding in holdings[:5]:  # 최대 5개만 표시
                print(f"  - {holding['name']}({holding['symbol']}): {holding['quantity']}주, {holding['evaluation_amount']:,.0f}원")
            
            # 4. 거래내역 조회
            print("\n4. 거래내역 조회")
            transactions = data_service.get_transactions(test_account_id)
            print(f"조회된 거래내역 수: {len(transactions)}")
            for transaction in transactions[:5]:  # 최대 5개만 표시
                print(f"  - {transaction['transaction_date']}: {transaction['name']}({transaction['symbol']}) {transaction['transaction_type']} {transaction['quantity']}주")
            
            # 5. 최근 거래내역 조회
            print("\n5. 최근 거래내역 조회 (5건)")
            recent_transactions = data_service.get_recent_transactions(test_account_id, limit=5)
            print(f"조회된 최근 거래내역 수: {len(recent_transactions)}")
            for transaction in recent_transactions:
                print(f"  - {transaction['transaction_date']}: {transaction['name']}({transaction['symbol']}) {transaction['transaction_type']} {transaction['quantity']}주")
        
        else:
            print("등록된 계좌가 없습니다.")
        
        print("\nSuccess: DataService 테스트 완료")
        
    except Exception as e:
        print(f"Error: 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_service()
