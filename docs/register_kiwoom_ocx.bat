@echo off
echo ========================================
echo Kiwoom OpenAPI OCX Registration
echo ========================================
echo.
echo This script must be run as Administrator!
echo.

regsvr32 "C:\OpenAPI\khopenapi.ocx"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] OCX registered successfully!
    echo.
    echo You can now test the connection:
    echo   cd "c:\Users\ghkdw\Desktop\개발 공부\Stock Analyzer"
    echo   python test_kiwoom_broker.py
) else (
    echo.
    echo [ERROR] Registration failed!
    echo Make sure you run this as Administrator.
)

pause
