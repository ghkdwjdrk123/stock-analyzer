"""
GUI용 차트 서비스
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.chart_generator import ChartGenerator
from gui.utils.data_service import DataService
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ChartService:
    """GUI용 차트 서비스"""
    
    def __init__(self):
        self.chart_generator = ChartGenerator()
        self.data_service = DataService()
    
    def create_portfolio_performance_chart(self, account_id: int, days: int = 30) -> Optional[str]:
        """포트폴리오 성과 차트 생성"""
        try:
            # 잔고 이력 데이터 조회
            balance_data = self.data_service.get_balance_history(account_id, days)
            
            if not balance_data:
                logger.warning(f"포트폴리오 성과 데이터 없음: account_id={account_id}")
                return None
            
            # 차트 생성
            fig = self.chart_generator.create_portfolio_performance_chart(balance_data)
            
            # HTML 파일로 저장
            filename = f"portfolio_performance_{account_id}_{date.today().strftime('%Y%m%d')}.html"
            filepath = self.chart_generator.export_chart_to_html(fig, filename)
            
            # HTML 내용 읽기
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return html_content
            
        except Exception as e:
            logger.error(f"포트폴리오 성과 차트 생성 실패: {str(e)}")
            return None
    
    def create_holdings_pie_chart(self, account_id: int) -> Optional[str]:
        """보유종목 비중 파이 차트 생성"""
        try:
            # 보유종목 데이터 조회
            holdings_data = self.data_service.get_holdings(account_id)
            
            if not holdings_data:
                logger.warning(f"보유종목 데이터 없음: account_id={account_id}")
                return None
            
            # 차트 생성
            fig = self.chart_generator.create_holdings_pie_chart(holdings_data)
            
            # HTML 파일로 저장
            filename = f"holdings_pie_{account_id}_{date.today().strftime('%Y%m%d')}.html"
            filepath = self.chart_generator.export_chart_to_html(fig, filename)
            
            # HTML 내용 읽기
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return html_content
            
        except Exception as e:
            logger.error(f"보유종목 비중 차트 생성 실패: {str(e)}")
            return None
    
    def create_holdings_performance_chart(self, account_id: int) -> Optional[str]:
        """보유종목 성과 차트 생성"""
        try:
            # 보유종목 데이터 조회
            holdings_data = self.data_service.get_holdings(account_id)
            
            if not holdings_data:
                logger.warning(f"보유종목 데이터 없음: account_id={account_id}")
                return None
            
            # 차트 생성
            fig = self.chart_generator.create_holdings_performance_chart(holdings_data)
            
            # HTML 파일로 저장
            filename = f"holdings_performance_{account_id}_{date.today().strftime('%Y%m%d')}.html"
            filepath = self.chart_generator.export_chart_to_html(fig, filename)
            
            # HTML 내용 읽기
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return html_content
            
        except Exception as e:
            logger.error(f"보유종목 성과 차트 생성 실패: {str(e)}")
            return None
    
    def create_monthly_return_chart(self, account_id: int, year: int) -> Optional[str]:
        """월별 수익률 차트 생성"""
        try:
            # 월별 데이터 조회
            monthly_data = []
            for month in range(1, 13):
                # 해당 월의 마지막 날짜
                if month == 12:
                    next_month = date(year + 1, 1, 1)
                else:
                    next_month = date(year, month + 1, 1)
                month_end = next_month - timedelta(days=1)
                
                # 해당 월의 잔고 데이터 조회
                balance_data = self.data_service.get_balance_history(
                    account_id, 
                    days=(month_end - date(year, month, 1)).days + 1
                )
                
                if balance_data:
                    # 해당 월의 마지막 데이터
                    latest_balance = balance_data[0]  # 가장 최근 데이터
                    monthly_data.append({
                        'month': f"{year}-{month:02d}",
                        'total_balance': latest_balance['total_balance'],
                        'profit_loss_rate': latest_balance['profit_loss_rate']
                    })
            
            if not monthly_data:
                logger.warning(f"월별 데이터 없음: account_id={account_id}, year={year}")
                return None
            
            # 차트 생성
            fig = self.chart_generator.create_monthly_summary_chart(monthly_data)
            
            # HTML 파일로 저장
            filename = f"monthly_return_{account_id}_{year}.html"
            filepath = self.chart_generator.export_chart_to_html(fig, filename)
            
            # HTML 내용 읽기
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            return html_content
            
        except Exception as e:
            logger.error(f"월별 수익률 차트 생성 실패: {str(e)}")
            return None
    
    def create_transaction_pattern_chart(self, account_id: int, days: int = 30) -> Optional[str]:
        """거래 패턴 차트 생성"""
        try:
            # 거래내역 데이터 조회
            transactions_data = self.data_service.get_transactions(account_id)
            
            if not transactions_data:
                logger.warning(f"거래내역 데이터 없음: account_id={account_id}")
                return None
            
            # 거래 패턴 분석을 위한 데이터 처리
            # (추후 구현)
            
            return None
            
        except Exception as e:
            logger.error(f"거래 패턴 차트 생성 실패: {str(e)}")
            return None
