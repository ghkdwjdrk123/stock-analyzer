@echo off
REM Stock Analyzer Database Command Shortcuts
REM Windows Batch Script for Quick Database Access

cd /d "%~dp0"

if "%1"=="" (
    echo ========================================
    echo   Stock Analyzer Database Commands
    echo ========================================
    echo.
    echo   db status      - DB 상태 및 전체 테이블 요약
    echo   db accounts    - 계좌 테이블 조회
    echo   db balances    - 잔고 테이블 조회
    echo   db holdings    - 보유종목 테이블 조회
    echo   db transactions- 거래내역 테이블 조회
    echo   db brokers     - 브로커 테이블 조회
    echo   db relations   - 테이블 관계 조회
    echo.
    echo   Quick Commands:
    echo   db latest      - 최신 데이터 조회
    echo   db top         - 상위 보유종목
    echo   db recent      - 최근 거래내역
    echo   db profit      - 수익률 요약
    echo.
    echo   Example:
    echo   db holdings --limit 20
    echo   db balances --account-id 1
    echo ========================================
    goto :end
)

if "%1"=="status" (
    python view_database.py --summary
    goto :end
)

if "%1"=="accounts" (
    python view_database.py accounts %2 %3 %4 %5
    goto :end
)

if "%1"=="balances" (
    python view_database.py balances %2 %3 %4 %5
    goto :end
)

if "%1"=="holdings" (
    python view_database.py holdings %2 %3 %4 %5
    goto :end
)

if "%1"=="transactions" (
    python view_database.py transactions %2 %3 %4 %5
    goto :end
)

if "%1"=="brokers" (
    python view_database.py brokers %2 %3 %4 %5
    goto :end
)

if "%1"=="relations" (
    python view_database.py --relations
    goto :end
)

if "%1"=="latest" (
    python db_commands.py latest
    goto :end
)

if "%1"=="top" (
    python db_commands.py holdings
    goto :end
)

if "%1"=="recent" (
    python db_commands.py transactions
    goto :end
)

if "%1"=="profit" (
    python db_commands.py performance
    goto :end
)

echo Unknown command: %1
echo Type 'db' without parameters to see available commands.

:end