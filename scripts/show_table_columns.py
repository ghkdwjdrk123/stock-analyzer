#!/usr/bin/env python3
"""
Stock Analyzer Database Table Columns Viewer
모든 테이블의 컬럼명과 데이터 타입을 출력하는 스크립트
"""

import sys
from pathlib import Path
from tabulate import tabulate
from sqlalchemy import inspect

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

def init_database():
    """데이터베이스 초기화"""
    try:
        config_manager = ConfigManager()
        config = config_manager.config
        database_config = config.get('database', {})
        database_url = get_database_url(database_config)
        db_manager.init_database(database_url)
        session = db_manager.get_session()
        print("SUCCESS: Database connection established")
        return session
    except Exception as e:
        print(f"ERROR: Database connection failed: {str(e)}")
        sys.exit(1)

def show_table_columns():
    """모든 테이블의 컬럼 정보 출력"""
    session = init_database()

    # 테이블과 모델 매핑
    tables_info = [
        ("brokers", Broker),
        ("accounts", Account),
        ("daily_balances", DailyBalance),
        ("holdings", Holding),
        ("transactions", Transaction),
        ("monthly_summaries", MonthlySummary),
        ("stock_performances", StockPerformance),
        ("portfolio_analyses", PortfolioAnalysis),
        ("trading_patterns", TradingPattern),
        ("risk_metrics", RiskMetrics)
    ]

    # SQLAlchemy Inspector 사용
    inspector = inspect(session.bind)

    for table_name, model_class in tables_info:
        print("=" * 100)
        print(f"TABLE: {table_name.upper()}")
        print("=" * 100)

        try:
            # 테이블 컬럼 정보 가져오기
            columns = inspector.get_columns(table_name)

            if not columns:
                print(f"INFO: No columns found for table {table_name}")
                continue

            # 컬럼 정보 테이블 생성
            column_data = []
            for i, col in enumerate(columns, 1):
                column_data.append([
                    i,
                    col['name'],
                    str(col['type']),
                    "YES" if col['nullable'] else "NO",
                    "YES" if col.get('primary_key', False) else "NO",
                    str(col['default']) if col['default'] is not None else ""
                ])

            # 테이블 출력
            print(tabulate(column_data,
                          headers=["#", "Column Name", "Data Type", "Nullable", "Primary Key", "Default"],
                          tablefmt="grid"))

            print(f"Total Columns: {len(columns)}")

        except Exception as e:
            print(f"ERROR: Failed to get columns for {table_name}: {str(e)}")

        print()  # 빈 줄 추가

    session.close()

def show_specific_table(table_name):
    """특정 테이블의 컬럼 정보만 출력"""
    session = init_database()
    inspector = inspect(session.bind)

    print("=" * 100)
    print(f"TABLE: {table_name.upper()}")
    print("=" * 100)

    try:
        columns = inspector.get_columns(table_name)

        if not columns:
            print(f"INFO: Table '{table_name}' not found or has no columns")
            return

        column_data = []
        for i, col in enumerate(columns, 1):
            column_data.append([
                i,
                col['name'],
                str(col['type']),
                "YES" if col['nullable'] else "NO",
                "YES" if col.get('primary_key', False) else "NO",
                str(col['default']) if col['default'] is not None else ""
            ])

        print(tabulate(column_data,
                      headers=["#", "Column Name", "Data Type", "Nullable", "Primary Key", "Default"],
                      tablefmt="grid"))

        print(f"Total Columns: {len(columns)}")

    except Exception as e:
        print(f"ERROR: {str(e)}")

    session.close()

def show_summary():
    """모든 테이블의 컬럼 수 요약"""
    session = init_database()
    inspector = inspect(session.bind)

    table_names = [
        "brokers", "accounts", "daily_balances", "holdings", "transactions",
        "monthly_summaries", "stock_performances", "portfolio_analyses",
        "trading_patterns", "risk_metrics"
    ]

    print("=" * 80)
    print("TABLE COLUMNS SUMMARY")
    print("=" * 80)

    summary_data = []
    total_columns = 0

    for table_name in table_names:
        try:
            columns = inspector.get_columns(table_name)
            column_count = len(columns)
            total_columns += column_count

            # 주요 컬럼들 (첫 5개만)
            main_columns = [col['name'] for col in columns[:5]]
            if len(columns) > 5:
                main_columns.append("...")

            summary_data.append([
                table_name,
                column_count,
                ", ".join(main_columns)
            ])

        except Exception as e:
            summary_data.append([
                table_name,
                "ERROR",
                str(e)
            ])

    print(tabulate(summary_data,
                  headers=["Table Name", "Column Count", "Main Columns"],
                  tablefmt="grid"))

    print(f"\nTotal Tables: {len(table_names)}")
    print(f"Total Columns: {total_columns}")

    session.close()

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("Usage: python show_table_columns.py [option/table_name]")
        print("\nOptions:")
        print("  all       - Show all table columns")
        print("  summary   - Show columns summary")
        print("  [table]   - Show specific table columns")
        print("\nAvailable tables:")
        print("  brokers, accounts, daily_balances, holdings, transactions")
        print("  monthly_summaries, stock_performances, portfolio_analyses")
        print("  trading_patterns, risk_metrics")
        return

    option = sys.argv[1].lower()

    if option == "all":
        show_table_columns()
    elif option == "summary":
        show_summary()
    else:
        # 특정 테이블 조회
        show_specific_table(option)

if __name__ == "__main__":
    main()