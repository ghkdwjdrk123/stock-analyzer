"""
차트 생성 유틸리티 클래스
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ChartGenerator:
    """차트 생성 클래스"""
    
    def __init__(self):
        self.default_colors = px.colors.qualitative.Set3
        self.chart_theme = {
            'layout': {
                'paper_bgcolor': 'white',
                'plot_bgcolor': 'white',
                'font': {'family': 'Arial, sans-serif', 'size': 12},
                'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50}
            }
        }
    
    def create_portfolio_performance_chart(self, daily_balances: List[Dict[str, Any]]) -> go.Figure:
        """포트폴리오 성과 차트 생성"""
        try:
            if not daily_balances:
                return self._create_empty_chart("포트폴리오 성과 데이터가 없습니다.")
            
            # DataFrame 생성
            df = pd.DataFrame(daily_balances)
            df['balance_date'] = pd.to_datetime(df['balance_date'])
            df = df.sort_values('balance_date')
            
            # 서브플롯 생성 (2개 행)
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('총 자산 변화', '일일 수익률'),
                vertical_spacing=0.1,
                row_heights=[0.7, 0.3]
            )
            
            # 총 자산 차트 (일일 데이터이므로 마커 중심, 점선 연결)
            fig.add_trace(
                go.Scatter(
                    x=df['balance_date'],
                    y=df['total_balance'],
                    mode='markers+lines' if len(df) > 1 else 'markers',
                    name='총 자산',
                    line=dict(color=self.default_colors[0], width=1.5, dash='dot'),
                    marker=dict(size=8, color=self.default_colors[0]),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                '날짜: %{x}<br>' +
                                '총 자산: %{y:,.0f}원<br>' +
                                '<extra></extra>'
                ),
                row=1, col=1
            )

            # 평가금액 차트 (일일 데이터이므로 마커 중심, 점선 연결)
            fig.add_trace(
                go.Scatter(
                    x=df['balance_date'],
                    y=df['evaluation_amount'],
                    mode='markers+lines' if len(df) > 1 else 'markers',
                    name='평가금액',
                    line=dict(color=self.default_colors[1], width=1.5, dash='dot'),
                    marker=dict(size=7, color=self.default_colors[1]),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                '날짜: %{x}<br>' +
                                '평가금액: %{y:,.0f}원<br>' +
                                '<extra></extra>'
                ),
                row=1, col=1
            )

            # 현금잔고 차트 (일일 데이터이므로 마커 중심, 점선 연결)
            fig.add_trace(
                go.Scatter(
                    x=df['balance_date'],
                    y=df['cash_balance'],
                    mode='markers+lines' if len(df) > 1 else 'markers',
                    name='현금잔고',
                    line=dict(color=self.default_colors[2], width=1.5, dash='dot'),
                    marker=dict(size=7, color=self.default_colors[2]),
                    hovertemplate='<b>%{fullData.name}</b><br>' +
                                '날짜: %{x}<br>' +
                                '현금잔고: %{y:,.0f}원<br>' +
                                '<extra></extra>'
                ),
                row=1, col=1
            )
            
            # 일일 수익률 차트
            fig.add_trace(
                go.Bar(
                    x=df['balance_date'],
                    y=df['profit_loss_rate'],
                    name='일일 수익률 (%)',
                    marker_color=['green' if x >= 0 else 'red' for x in df['profit_loss_rate']],
                    hovertemplate='<b>일일 수익률</b><br>' +
                                '날짜: %{x}<br>' +
                                '수익률: %{y:.2f}%<br>' +
                                '<extra></extra>'
                ),
                row=2, col=1
            )
            
            # 레이아웃 설정
            fig.update_layout(
                title={
                    'text': '포트폴리오 성과 분석',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20}
                },
                height=600,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                **self.chart_theme['layout']
            )
            
            # Y축 포맷팅
            fig.update_yaxes(tickformat=',.0f', row=1, col=1)
            fig.update_yaxes(tickformat='.2f', row=2, col=1)
            
            # X축 설정
            fig.update_xaxes(title_text="날짜", row=2, col=1)
            
            logger.info("포트폴리오 성과 차트 생성 완료")
            return fig
            
        except Exception as e:
            logger.error(f"포트폴리오 성과 차트 생성 실패: {str(e)}")
            return self._create_error_chart(str(e))
    
    def create_holdings_pie_chart(self, holdings: List[Dict[str, Any]]) -> go.Figure:
        """보유종목 비중 파이 차트 생성"""
        try:
            if not holdings:
                return self._create_empty_chart("보유종목 데이터가 없습니다.")
            
            # DataFrame 생성
            df = pd.DataFrame(holdings)
            
            # 평가금액이 0인 종목 제외
            df = df[df['evaluation_amount'] > 0]
            
            if df.empty:
                return self._create_empty_chart("보유중인 종목이 없습니다.")
            
            # 파이 차트 생성
            fig = go.Figure(data=[go.Pie(
                labels=df['name'],
                values=df['evaluation_amount'],
                textinfo='label+percent',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>' +
                            '평가금액: %{value:,.0f}원<br>' +
                            '비중: %{percent}<br>' +
                            '<extra></extra>',
                marker=dict(colors=self.default_colors)
            )])
            
            fig.update_layout(
                title={
                    'text': '보유종목 비중 분석',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20}
                },
                height=500,
                **self.chart_theme['layout']
            )
            
            logger.info("보유종목 비중 차트 생성 완료")
            return fig
            
        except Exception as e:
            logger.error(f"보유종목 비중 차트 생성 실패: {str(e)}")
            return self._create_error_chart(str(e))
    
    def create_holdings_performance_chart(self, holdings: List[Dict[str, Any]]) -> go.Figure:
        """보유종목 성과 차트 생성"""
        try:
            if not holdings:
                return self._create_empty_chart("보유종목 데이터가 없습니다.")
            
            # DataFrame 생성
            df = pd.DataFrame(holdings)
            df = df.sort_values('profit_loss_rate', ascending=False)
            
            # 막대 차트 생성
            fig = go.Figure()
            
            # 수익률별 색상 설정
            colors = ['green' if x >= 0 else 'red' for x in df['profit_loss_rate']]
            
            fig.add_trace(go.Bar(
                x=df['name'],
                y=df['profit_loss_rate'],
                marker_color=colors,
                text=[f"{x:.2f}%" for x in df['profit_loss_rate']],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>' +
                            '수익률: %{y:.2f}%<br>' +
                            '평가금액: %{customdata:,.0f}원<br>' +
                            '<extra></extra>',
                customdata=df['evaluation_amount']
            ))
            
            fig.update_layout(
                title={
                    'text': '보유종목별 수익률',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20}
                },
                xaxis_title="종목명",
                yaxis_title="수익률 (%)",
                height=500,
                **self.chart_theme['layout']
            )
            
            # X축 레이블 회전
            fig.update_xaxes(tickangle=45)
            
            logger.info("보유종목 성과 차트 생성 완료")
            return fig
            
        except Exception as e:
            logger.error(f"보유종목 성과 차트 생성 실패: {str(e)}")
            return self._create_error_chart(str(e))
    
    def create_monthly_summary_chart(self, monthly_data: List[Dict[str, Any]]) -> go.Figure:
        """월별 요약 차트 생성"""
        try:
            if not monthly_data:
                return self._create_empty_chart("월별 데이터가 없습니다.")
            
            # DataFrame 생성
            df = pd.DataFrame(monthly_data)
            df['month'] = pd.to_datetime(df['month'])
            df = df.sort_values('month')
            
            # 서브플롯 생성 (2개 행)
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('월별 총 자산', '월별 수익률'),
                vertical_spacing=0.1,
                row_heights=[0.6, 0.4]
            )
            
            # 월별 총 자산
            fig.add_trace(
                go.Bar(
                    x=df['month'],
                    y=df['total_balance'],
                    name='총 자산',
                    marker_color=self.default_colors[0],
                    hovertemplate='<b>총 자산</b><br>' +
                                '월: %{x}<br>' +
                                '총 자산: %{y:,.0f}원<br>' +
                                '<extra></extra>'
                ),
                row=1, col=1
            )
            
            # 월별 수익률
            colors = ['green' if x >= 0 else 'red' for x in df['profit_loss_rate']]
            fig.add_trace(
                go.Bar(
                    x=df['month'],
                    y=df['profit_loss_rate'],
                    name='월 수익률 (%)',
                    marker_color=colors,
                    hovertemplate='<b>월 수익률</b><br>' +
                                '월: %{x}<br>' +
                                '수익률: %{y:.2f}%<br>' +
                                '<extra></extra>'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title={
                    'text': '월별 포트폴리오 요약',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20}
                },
                height=600,
                showlegend=False,
                **self.chart_theme['layout']
            )
            
            # Y축 포맷팅
            fig.update_yaxes(tickformat=',.0f', row=1, col=1)
            fig.update_yaxes(tickformat='.2f', row=2, col=1)
            
            # X축 설정
            fig.update_xaxes(title_text="월", row=2, col=1)
            
            logger.info("월별 요약 차트 생성 완료")
            return fig
            
        except Exception as e:
            logger.error(f"월별 요약 차트 생성 실패: {str(e)}")
            return self._create_error_chart(str(e))
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """빈 데이터용 차트 생성"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        fig.update_layout(**self.chart_theme['layout'])
        return fig
    
    def _create_error_chart(self, error_message: str) -> go.Figure:
        """에러용 차트 생성"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"차트 생성 오류:<br>{error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=14, font_color='red'
        )
        fig.update_layout(**self.chart_theme['layout'])
        return fig
    
    def export_chart_to_html(self, fig: go.Figure, filename: str) -> str:
        """차트를 HTML 파일로 내보내기"""
        try:
            filepath = f"./data/charts/{filename}"
            fig.write_html(filepath)
            logger.info(f"차트 HTML 내보내기 완료: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"차트 HTML 내보내기 실패: {str(e)}")
            raise
    
    def export_chart_to_image(self, fig: go.Figure, filename: str, format: str = 'png') -> str:
        """차트를 이미지 파일로 내보내기"""
        try:
            filepath = f"./data/charts/{filename}.{format}"
            fig.write_image(filepath)
            logger.info(f"차트 이미지 내보내기 완료: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"차트 이미지 내보내기 실패: {str(e)}")
            raise
