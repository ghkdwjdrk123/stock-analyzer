#!/usr/bin/env python3
"""
Stock Analyzer Database Quick Commands
간단한 DB 조회 명령어들

빠른 조회용 명령어 모음
"""

import sys
from pathlib import Path
from tabulate import tabulate

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from view_database import DatabaseViewer

class QuickCommands:
    """빠른 명령어 클래스"""

    def __init__(self):
        self.viewer = DatabaseViewer()

    def status(self):
        """DB 상태 조회"""
        print("🔍 Stock Analyzer Database Status")
        self.viewer.show_table_summary()

    def accounts_summary(self):
        """계좌 요약"""
        accounts = self.viewer.session.query(
            self.viewer.session.query().from_statement("""
            SELECT a.id, a.account_number, b.name as broker_name, a.is_active,
                   COUNT(DISTINCT db.id) as balance_records,
                   COUNT(DISTINCT h.id) as holdings_count,
                   COUNT(DISTINCT t.id) as transactions_count
            FROM accounts a
            LEFT JOIN brokers b ON a.broker_id = b.id
            LEFT JOIN daily_balances db ON a.id = db.account_id
            LEFT JOIN holdings h ON a.id = h.account_id AND h.quantity > 0
            LEFT JOIN transactions t ON a.id = t.account_id
            GROUP BY a.id, a.account_number, b.name, a.is_active
            """)
        ).all()

        print("📊 계좌별 데이터 현황")
        print("=" * 80)

    def latest_data(self):
        """최신 데이터 조회"""
        print("📅 최신 데이터 현황")
        print("=" * 50)

        # 최신 잔고 데이터
        from app.models.balance import DailyBalance
        from app.models.account import Account
        from app.models.broker import Broker

        latest_balance = self.viewer.session.query(DailyBalance, Account, Broker)\
            .join(Account).join(Broker)\
            .order_by(DailyBalance.balance_date.desc())\
            .first()

        if latest_balance:
            balance, account, broker = latest_balance
            print(f"💰 최신 잔고: {balance.balance_date} ({broker.name}-{account.account_number})")
            print(f"   총 잔고: {balance.total_balance:,.0f}원")
            print(f"   손익: {balance.profit_loss:,.0f}원 ({balance.profit_loss_rate:.2f}%)")

        # 최신 거래
        from app.models.transaction import Transaction

        latest_transaction = self.viewer.session.query(Transaction, Account, Broker)\
            .join(Account).join(Broker)\
            .order_by(Transaction.transaction_date.desc())\
            .first()

        if latest_transaction:
            transaction, account, broker = latest_transaction
            print(f"📊 최신 거래: {transaction.transaction_date} ({broker.name}-{account.account_number})")
            print(f"   종목: {transaction.name} ({transaction.symbol})")
            print(f"   거래: {'매수' if transaction.transaction_type == 'BUY' else '매도'} {transaction.quantity:,}주")

    def top_holdings(self, limit=10):
        """상위 보유종목"""
        from app.models.holding import Holding
        from app.models.account import Account
        from app.models.broker import Broker

        holdings = self.viewer.session.query(Holding, Account, Broker)\
            .join(Account).join(Broker)\
            .filter(Holding.quantity > 0)\
            .order_by(Holding.evaluation_amount.desc())\
            .limit(limit).all()

        if not holdings:
            print("❌ 보유종목 데이터가 없습니다.")
            return

        print(f"🏆 상위 {limit}개 보유종목")
        print("=" * 80)

        data = []
        for holding, account, broker in holdings:
            data.append([
                holding.symbol,
                holding.name,
                f"{holding.quantity:,}",
                f"{holding.evaluation_amount:,.0f}",
                f"{holding.profit_loss_rate:.1f}%"
            ])

        print(tabulate(data,
                      headers=["종목코드", "종목명", "수량", "평가액", "수익률"],
                      tablefmt="simple"))

    def recent_transactions(self, limit=10):
        """최근 거래내역"""
        from app.models.transaction import Transaction
        from app.models.account import Account
        from app.models.broker import Broker

        transactions = self.viewer.session.query(Transaction, Account, Broker)\
            .join(Account).join(Broker)\
            .order_by(Transaction.transaction_date.desc())\
            .limit(limit).all()

        if not transactions:
            print("❌ 거래내역이 없습니다.")
            return

        print(f"📈 최근 {limit}개 거래내역")
        print("=" * 80)

        data = []
        for transaction, account, broker in transactions:
            data.append([
                transaction.transaction_date.strftime("%m-%d"),
                transaction.symbol,
                "매수" if transaction.transaction_type == "BUY" else "매도",
                f"{transaction.quantity:,}",
                f"{transaction.amount:,.0f}"
            ])

        print(tabulate(data,
                      headers=["날짜", "종목", "구분", "수량", "금액"],
                      tablefmt="simple"))

    def performance_summary(self):
        """수익률 요약"""
        from app.models.balance import DailyBalance
        from app.models.account import Account
        from app.models.broker import Broker
        from sqlalchemy import func

        # 계좌별 수익률 요약
        performance = self.viewer.session.query(
            Account.id,
            Broker.name.label('broker_name'),
            Account.account_number,
            func.max(DailyBalance.total_balance).label('latest_balance'),
            func.max(DailyBalance.profit_loss).label('latest_profit_loss'),
            func.max(DailyBalance.profit_loss_rate).label('latest_profit_rate')
        ).join(Broker).join(DailyBalance)\
         .group_by(Account.id, Broker.name, Account.account_number)\
         .all()

        if not performance:
            print("❌ 수익률 데이터가 없습니다.")
            return

        print("💹 계좌별 수익률 현황")
        print("=" * 70)

        data = []
        total_balance = 0
        total_profit = 0

        for perf in performance:
            total_balance += perf.latest_balance or 0
            total_profit += perf.latest_profit_loss or 0

            data.append([
                f"{perf.broker_name}-{perf.account_number}",
                f"{perf.latest_balance:,.0f}" if perf.latest_balance else "0",
                f"{perf.latest_profit_loss:,.0f}" if perf.latest_profit_loss else "0",
                f"{perf.latest_profit_rate:.2f}%" if perf.latest_profit_rate else "0.00%"
            ])

        print(tabulate(data,
                      headers=["계좌", "총잔고", "손익", "수익률"],
                      tablefmt="simple"))

        # 전체 요약
        overall_rate = (total_profit / total_balance * 100) if total_balance > 0 else 0
        print(f"\n📊 전체 요약:")
        print(f"   총 잔고: {total_balance:,.0f}원")
        print(f"   총 손익: {total_profit:,.0f}원")
        print(f"   전체 수익률: {overall_rate:.2f}%")

    def close(self):
        """리소스 정리"""
        self.viewer.close()

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python db_commands.py [명령어]")
        print("\n사용 가능한 명령어:")
        print("  status        - DB 상태 조회")
        print("  latest        - 최신 데이터 조회")
        print("  holdings      - 상위 보유종목")
        print("  transactions  - 최근 거래내역")
        print("  performance   - 수익률 요약")
        return

    command = sys.argv[1].lower()
    commands = QuickCommands()

    try:
        if command == "status":
            commands.status()
        elif command == "latest":
            commands.latest_data()
        elif command in ["holdings", "top"]:
            commands.top_holdings()
        elif command in ["transactions", "recent"]:
            commands.recent_transactions()
        elif command in ["performance", "profit"]:
            commands.performance_summary()
        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print("사용 가능한 명령어: status, latest, holdings, transactions, performance")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    finally:
        commands.close()

if __name__ == "__main__":
    main()