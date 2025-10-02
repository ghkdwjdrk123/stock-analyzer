#!/usr/bin/env python3
"""
Stock Analyzer Database Viewer
DB :
    python view_database.py [] []

:
    python view_database.py                    # python view_database.py brokers            # python view_database.py accounts           # python view_database.py balances           # python view_database.py holdings           # python view_database.py transactions       # python view_database.py --summary          # python view_database.py --relations        # """

import sys
import argparse
from pathlib import Path
from datetime import datetime, date
from tabulate import tabulate
from typing import List, Dict, Any, Optional

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.database import db_manager, get_database_url
from app.utils.config import ConfigManager
from app.models.broker import Broker
from app.models.account import Account
from app.models.balance import DailyBalance
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.models.aggregation import (
    MonthlySummary, StockPerformance, PortfolioAnalysis,
    TradingPattern, RiskMetrics
)

class DatabaseViewer:
    """"""

    def __init__(self):
        self.session = None
        self._init_database()

    def _init_database(self):
        """"""
        try:
            config_manager = ConfigManager()
            config = config_manager.config
            database_config = config.get('database', {})
            database_url = get_database_url(database_config)
            db_manager.init_database(database_url)
            self.session = db_manager.get_session()
            print("SUCCESS: Database connection established")
        except Exception as e:
            print(f"ERROR: Database connection failed: {str(e)}")
            sys.exit(1)

    def format_datetime(self, dt) -> str:
        """/"""
        if dt is None:
            return ""
        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(dt, date):
            return dt.strftime("%Y-%m-%d")
        return str(dt)

    def format_float(self, value) -> str:
        """"""
        if value is None:
            return ""
        if isinstance(value, (int, float)):
            if abs(value) >= 1000:
                return f"{value:,.0f}"
            else:
                return f"{value:.2f}"
        return str(value)

    def format_boolean(self, value) -> str:
        """"""
        if value is None:
            return ""
        return "YES" if value else "NO"

    def show_table_summary(self):
        """"""
        tables_info = [
            ("brokers", Broker, "Broker Info"),
            ("accounts", Account, "Account Info"),
            ("daily_balances", DailyBalance, "Daily Balance"),
            ("holdings", Holding, "Holdings"),
            ("transactions", Transaction, "Transactions"),
            ("monthly_summaries", MonthlySummary, "Monthly Summary"),
            ("stock_performances", StockPerformance, "Stock Performance"),
            ("portfolio_analyses", PortfolioAnalysis, "Portfolio Analysis"),
            ("trading_patterns", TradingPattern, "Trading Patterns"),
            ("risk_metrics", RiskMetrics, "Risk Metrics")
        ]

        summary_data = []
        total_records = 0

        for table_name, model_class, description in tables_info:
            try:
                count = self.session.query(model_class).count()
                total_records += count
                summary_data.append([
                    table_name,
                    description,
                    f"{count:,}",
                    "OK" if count > 0 else "EMPTY"
                ])
            except Exception as e:
                summary_data.append([
                    table_name,
                    description,
                    "ERROR",
                    f"FAILED: {str(e)}"
                ])

        print("=" * 80)
        print("STOCK ANALYZER DATABASE SUMMARY")
        print("=" * 80)
        print(tabulate(summary_data,
                      headers=["Table Name", "Description", "Records", "Status"],
                      tablefmt="grid"))
        print(f"\nTotal Records: {total_records:,}")
        print(f"Query Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def show_brokers(self, limit: Optional[int] = None):
        """"""
        query = self.session.query(Broker)
        if limit:
            query = query.limit(limit)

        brokers = query.all()

        if not brokers:
            print(".")
            return

        data = []
        for broker in brokers:
            data.append([
                broker.id,
                broker.name,
                broker.api_type,
                broker.platform,
                self.format_boolean(broker.enabled),
                broker.description or "",
                self.format_datetime(broker.created_at)
            ])

        print("=" * 100)
        print("BROKERS TABLE")
        print("=" * 100)
        print(tabulate(data,
                      headers=["ID", "Name", "API Type", "Platform", "Enabled", "Description", "Created"],
                      tablefmt="grid"))
        print(f"{len(brokers)}")

    def show_accounts(self, limit: Optional[int] = None):
        """"""
        query = self.session.query(Account, Broker).join(Broker, Account.broker_id == Broker.id)
        if limit:
            query = query.limit(limit)

        accounts = query.all()

        if not accounts:
            print(".")
            return

        data = []
        for account, broker in accounts:
            data.append([
                account.id,
                broker.name,
                account.account_number,
                account.account_name or "",
                account.account_type,
                self.format_boolean(account.is_active),
                self.format_datetime(account.created_at)
            ])

        print("=" * 120)
        print("ACCOUNTS TABLE")
        print("=" * 120)
        print(tabulate(data,
                      headers=["ID", "Broker", "Account No", "Account Name", "Type", "Active", "Created"],
                      tablefmt="grid"))
        print(f"{len(accounts)}")

    def show_balances(self, limit: Optional[int] = None, account_id: Optional[int] = None):
        """"""
        query = self.session.query(DailyBalance, Account, Broker)\
            .join(Account, DailyBalance.account_id == Account.id)\
            .join(Broker, Account.broker_id == Broker.id)\
            .order_by(DailyBalance.balance_date.desc())

        if account_id:
            query = query.filter(DailyBalance.account_id == account_id)

        if limit:
            query = query.limit(limit)

        balances = query.all()

        if not balances:
            print(".")
            return

        data = []
        for balance, account, broker in balances:
            data.append([
                self.format_datetime(balance.balance_date),
                broker.name,
                account.account_number,
                self.format_float(balance.total_balance),
                self.format_float(balance.cash_balance),
                self.format_float(balance.stock_balance),
                self.format_float(balance.profit_loss),
                f"{balance.profit_loss_rate:.2f}%" if balance.profit_loss_rate else "0.00%"
            ])

        print("=" * 130)
        print("DAILY BALANCES TABLE")
        print("=" * 130)
        print(tabulate(data,
                      headers=["Date", "Broker", "Account No", "Total", "Cash", "Stock", "P&L", "Rate"],
                      tablefmt="grid"))
        print(f"{len(balances)}")

    def show_holdings(self, limit: Optional[int] = None, account_id: Optional[int] = None):
        """"""
        query = self.session.query(Holding, Account, Broker)\
            .join(Account, Holding.account_id == Account.id)\
            .join(Broker, Account.broker_id == Broker.id)\
            .filter(Holding.quantity > 0)\
            .order_by(Holding.evaluation_amount.desc())

        if account_id:
            query = query.filter(Holding.account_id == account_id)

        if limit:
            query = query.limit(limit)

        holdings = query.all()

        if not holdings:
            print("INFO: No holdings data found.")
            return

        data = []
        for holding, account, broker in holdings:
            data.append([
                broker.name,
                account.account_number,
                holding.symbol,
                holding.name,
                f"{holding.quantity:,}",
                self.format_float(holding.average_price),
                self.format_float(holding.current_price),
                self.format_float(holding.evaluation_amount),
                self.format_float(holding.profit_loss),
                f"{holding.profit_loss_rate:.2f}%" if holding.profit_loss_rate else "0.00%"
            ])

        print("=" * 150)
        print("HOLDINGS TABLE")
        print("=" * 150)
        print(tabulate(data,
                      headers=["Broker", "Account No", "Symbol", "Name", "Quantity", "Avg Price", "Current", "Value", "P&L", "Rate"],
                      tablefmt="grid"))
        print(f"Total: {len(holdings)} holdings")

    def show_transactions(self, limit: Optional[int] = None, account_id: Optional[int] = None):
        """"""
        query = self.session.query(Transaction, Account, Broker)\
            .join(Account, Transaction.account_id == Account.id)\
            .join(Broker, Account.broker_id == Broker.id)\
            .order_by(Transaction.transaction_date.desc())

        if account_id:
            query = query.filter(Transaction.account_id == account_id)

        if limit:
            query = query.limit(limit)

        transactions = query.all()

        if not transactions:
            print(".")
            return

        data = []
        for transaction, account, broker in transactions:
            data.append([
                self.format_datetime(transaction.transaction_date),
                broker.name,
                account.account_number,
                transaction.symbol,
                transaction.name,
                "Buy" if transaction.transaction_type == "BUY" else "Sell",
                f"{transaction.quantity:,}",
                self.format_float(transaction.price),
                self.format_float(transaction.amount),
                self.format_float(transaction.fee)
            ])

        print("=" * 150)
        print("TRANSACTIONS TABLE")
        print("=" * 150)
        print(tabulate(data,
                      headers=["Date", "Broker", "Account No", "Symbol", "Name", "Type", "Quantity", "Price", "Amount", "Fee"],
                      tablefmt="grid"))
        print(f"{len(transactions)}")

    def show_monthly_summaries(self, limit: Optional[int] = None):
        """"""
        query = self.session.query(MonthlySummary, Account, Broker)\
            .join(Account, MonthlySummary.account_id == Account.id)\
            .join(Broker, Account.broker_id == Broker.id)\
            .order_by(MonthlySummary.year.desc(), MonthlySummary.month.desc())

        if limit:
            query = query.limit(limit)

        summaries = query.all()

        if not summaries:
            print(".")
            return

        data = []
        for summary, account, broker in summaries:
            data.append([
                f"{summary.year}-{summary.month:02d}",
                broker.name,
                account.account_number,
                self.format_float(summary.total_balance),
                self.format_float(summary.total_profit_loss),
                f"{summary.profit_loss_rate:.2f}%" if summary.profit_loss_rate else "0.00%",
                f"{summary.total_transactions:,}",
                f"{summary.total_holdings:,}",
                f"{summary.sharpe_ratio:.2f}" if summary.sharpe_ratio else "0.00"
            ])

        print("=" * 140)
        print("MONTHLY SUMMARIES TABLE")
        print("=" * 140)
        print(tabulate(data,
                      headers=["Year-Month", "Broker", "Account No", "Balance", "P&L", "Rate", "Transactions", "Holdings", "Sharpe"],
                      tablefmt="grid"))
        print(f"{len(summaries)}")

    def show_stock_performances(self, limit: Optional[int] = None):
        """"""
        query = self.session.query(StockPerformance, Account, Broker)\
            .join(Account, StockPerformance.account_id == Account.id)\
            .join(Broker, Account.broker_id == Broker.id)\
            .order_by(StockPerformance.profit_loss_rate.desc())

        if limit:
            query = query.limit(limit)

        performances = query.all()

        if not performances:
            print(".")
            return

        data = []
        for perf, account, broker in performances:
            data.append([
                broker.name,
                account.account_number,
                perf.symbol,
                perf.name,
                self.format_float(perf.total_investment),
                self.format_float(perf.current_value),
                self.format_float(perf.total_profit_loss),
                f"{perf.profit_loss_rate:.2f}%" if perf.profit_loss_rate else "0.00%",
                f"{perf.holding_days}" if perf.holding_days else ""
            ])

        print("=" * 140)
        print("STOCK PERFORMANCES TABLE")
        print("=" * 140)
        print(tabulate(data,
                      headers=["Broker", "Account No", "Symbol", "Name", "Investment", "Current", "P&L", "Rate", "Days"],
                      tablefmt="grid"))
        print(f"{len(performances)}")

    def show_table_relations(self):
        """"""
        relations_data = [
            ["brokers", "accounts", "1:N", "broker_id", "Broker-Account"],
            ["accounts", "daily_balances", "1:N", "account_id", "Account-Daily Balance"],
            ["accounts", "holdings", "1:N", "account_id", "Account-Holdings"],
            ["accounts", "transactions", "1:N", "account_id", "Account-Transactions"],
            ["accounts", "monthly_summaries", "1:N", "account_id", "Account-Monthly Summary"],
            ["accounts", "stock_performances", "1:N", "account_id", "Account-Stock Performance"],
            ["accounts", "portfolio_analyses", "1:N", "account_id", "Account-Portfolio Analysis"],
            ["accounts", "trading_patterns", "1:N", "account_id", "Account-Trading Patterns"],
            ["accounts", "risk_metrics", "1:N", "account_id", "Account-Risk Metrics"]
        ]

        print("=" * 100)
        print("TABLE RELATIONS")
        print("=" * 100)
        print(tabulate(relations_data,
                      headers=["Parent Table", "Child Table", "Relation", "Foreign Key", "Description"],
                      tablefmt="grid"))

    def close(self):
        """"""
        if self.session:
            self.session.close()

def main():
    parser = argparse.ArgumentParser(description="Stock Analyzer Database Viewer")
    parser.add_argument("table", nargs="?", help="")
    parser.add_argument("--limit", "-l", type=int, default=50, help="(: 50)")
    parser.add_argument("--account-id", "-a", type=int, help="ID")
    parser.add_argument("--summary", "-s", action="store_true", help="")
    parser.add_argument("--relations", "-r", action="store_true", help="")
    parser.add_argument("--all", action="store_true", help="(limit )")

    args = parser.parse_args()

    viewer = DatabaseViewer()

    try:
        if args.summary:
            viewer.show_table_summary()
        elif args.relations:
            viewer.show_table_relations()
        elif not args.table:
            print(":")
            print("  python view_database.py --summary          # ")
            print("  python view_database.py --relations        # ")
            print("  python view_database.py brokers            # ")
            print("  python view_database.py accounts           # ")
            print("  python view_database.py balances           # ")
            print("  python view_database.py holdings           # ")
            print("  python view_database.py transactions       # ")
            print("  python view_database.py monthly            # ")
            print("  python view_database.py performances       # ")
            print("\n:")
            print("  --limit N, -l N      # N")
            print("  --account-id N, -a N # ")
            print("  --all                # ")
            viewer.show_table_summary()
        else:
            limit = None if args.all else args.limit

            if args.table in ["brokers", "broker"]:
                viewer.show_brokers(limit)
            elif args.table in ["accounts", "account"]:
                viewer.show_accounts(limit)
            elif args.table in ["balances", "balance"]:
                viewer.show_balances(limit, args.account_id)
            elif args.table in ["holdings", "holding"]:
                viewer.show_holdings(limit, args.account_id)
            elif args.table in ["transactions", "transaction"]:
                viewer.show_transactions(limit, args.account_id)
            elif args.table in ["monthly", "summaries"]:
                viewer.show_monthly_summaries(limit)
            elif args.table in ["performances", "performance"]:
                viewer.show_stock_performances(limit)
            else:
                print(f"ERROR: Unknown table: {args.table}")
                print("Available tables: brokers, accounts, balances, holdings, transactions, monthly, performances")

    except KeyboardInterrupt:
        print("\n\nINTERRUPTED: Stopped by user")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        viewer.close()

if __name__ == "__main__":
    main()