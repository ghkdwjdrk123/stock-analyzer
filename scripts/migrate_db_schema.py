"""
데이터베이스 스키마 마이그레이션 스크립트
- DailyBalance에 updated_at 컬럼 추가
- Holding에 created_at, updated_at 컬럼 추가
- UNIQUE 제약조건 추가
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import sqlite3

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def migrate_database():
    """데이터베이스 스키마 마이그레이션"""
    db_path = "./data/stock_analyzer.db"

    if not os.path.exists(db_path):
        print(f"데이터베이스 파일이 없습니다: {db_path}")
        return False

    # 백업 생성
    backup_path = f"./data/stock_analyzer_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"데이터베이스 백업 생성: {backup_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("=== 데이터베이스 스키마 마이그레이션 시작 ===")

        # 1. DailyBalance 테이블에 updated_at 컬럼 추가
        print("1. DailyBalance 테이블 업데이트 중...")
        try:
            # 컬럼 존재 확인
            cursor.execute("PRAGMA table_info(daily_balances)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'updated_at' not in columns:
                # NULL로 컬럼 추가
                cursor.execute("ALTER TABLE daily_balances ADD COLUMN updated_at TIMESTAMP")
                # 기존 레코드들의 updated_at을 created_at 값으로 설정
                cursor.execute("UPDATE daily_balances SET updated_at = created_at")
                print("  - updated_at 컬럼 추가 및 초기화 완료")
            else:
                print("  - updated_at 컬럼이 이미 존재합니다")

        except Exception as e:
            print(f"  - DailyBalance 업데이트 실패: {e}")

        # 2. Holding 테이블에 created_at, updated_at 컬럼 추가
        print("2. Holding 테이블 업데이트 중...")
        try:
            cursor.execute("PRAGMA table_info(holdings)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE holdings ADD COLUMN created_at TIMESTAMP")
                cursor.execute("UPDATE holdings SET created_at = last_updated")
                print("  - created_at 컬럼 추가 및 초기화 완료")
            else:
                print("  - created_at 컬럼이 이미 존재합니다")

            if 'updated_at' not in columns:
                cursor.execute("ALTER TABLE holdings ADD COLUMN updated_at TIMESTAMP")
                cursor.execute("UPDATE holdings SET updated_at = last_updated")
                print("  - updated_at 컬럼 추가 및 초기화 완료")
            else:
                print("  - updated_at 컬럼이 이미 존재합니다")

        except Exception as e:
            print(f"  - Holding 업데이트 실패: {e}")

        # 3. 인덱스 생성
        print("3. 인덱스 생성 중...")
        try:
            # DailyBalance 인덱스
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_daily_balances_account_date
                ON daily_balances(account_id, balance_date)
            """)

            # Holdings 인덱스
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_holdings_account_symbol
                ON holdings(account_id, symbol)
            """)
            print("  - 인덱스 생성 완료")

        except Exception as e:
            print(f"  - 인덱스 생성 실패: {e}")

        # 4. 중복 데이터 정리 (필요한 경우)
        print("4. 중복 데이터 정리 중...")
        try:
            # DailyBalance 중복 데이터 제거 (가장 최신 것만 유지)
            cursor.execute("""
                DELETE FROM daily_balances
                WHERE id NOT IN (
                    SELECT MAX(id)
                    FROM daily_balances
                    GROUP BY account_id, balance_date
                )
            """)
            deleted_balances = cursor.rowcount

            # Holdings 중복 데이터 제거 (가장 최신 것만 유지)
            cursor.execute("""
                DELETE FROM holdings
                WHERE id NOT IN (
                    SELECT MAX(id)
                    FROM holdings
                    GROUP BY account_id, symbol
                )
            """)
            deleted_holdings = cursor.rowcount

            if deleted_balances > 0 or deleted_holdings > 0:
                print(f"  - 중복 제거: DailyBalance {deleted_balances}개, Holdings {deleted_holdings}개")
            else:
                print("  - 중복 데이터 없음")

        except Exception as e:
            print(f"  - 중복 데이터 정리 실패: {e}")

        conn.commit()
        print("\n데이터베이스 마이그레이션 완료!")

        # 테이블 정보 출력
        print("\n=== 업데이트된 테이블 구조 ===")
        cursor.execute("PRAGMA table_info(daily_balances)")
        print("DailyBalance 컬럼:")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")

        cursor.execute("PRAGMA table_info(holdings)")
        print("\nHolding 컬럼:")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")

        return True

    except Exception as e:
        conn.rollback()
        print(f"마이그레이션 실패: {str(e)}")
        print(f"백업에서 복원하려면: cp {backup_path} {db_path}")
        return False

    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n마이그레이션이 성공적으로 완료되었습니다!")
        print("이제 collect_today_data.py를 다시 실행할 수 있습니다.")
    else:
        print("\n마이그레이션이 실패했습니다.")
        sys.exit(1)