"""
Stock Analyzer GUI 실행 스크립트
"""
import subprocess
import sys
from pathlib import Path

def main():
    """GUI 실행"""
    try:
        # Streamlit 앱 실행
        gui_path = Path(__file__).parent / "gui" / "main.py"
        
        print("Stock Analyzer GUI를 시작합니다...")
        print(f"GUI 경로: {gui_path}")
        print("브라우저에서 http://localhost:8501 을 열어주세요.")
        print("종료하려면 Ctrl+C를 누르세요.")
        print("-" * 50)
        
        # Streamlit 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(gui_path),
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\nStock Analyzer GUI를 종료합니다.")
    except Exception as e:
        print(f"GUI 실행 중 오류가 발생했습니다: {str(e)}")
        print("requirements.txt의 패키지들이 설치되어 있는지 확인해주세요.")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
