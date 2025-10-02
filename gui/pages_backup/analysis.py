"""
분석 차트 페이지
"""
import streamlit as st
from gui.utils.data_service import DataService
from gui.utils.chart_service import ChartService

def main():
    """분석 차트 페이지"""
    st.title("Analysis Charts")
    
    # 계좌 ID 확인 (다중 선택 지원)
    selected_account_ids = st.session_state.get('selected_account_ids', [])

    if not selected_account_ids:
        st.warning("Warning: Please select an account from the sidebar first.")
        return

    # 현재는 첫 번째 선택된 계좌를 사용
    account_id = selected_account_ids[0]

    if len(selected_account_ids) > 1:
        st.info(f"Note: Showing data for the first selected account ({account_id}).")
    
    # 데이터 서비스 초기화
    data_service = DataService()
    chart_service = ChartService()
    
    try:
        # 차트 타입 선택
        st.subheader("Chart Type Selection")
        
        chart_type = st.selectbox(
            "분석할 차트를 선택하세요",
            [
                "포트폴리오 성과",
                "보유종목 비중",
                "보유종목 수익률",
                "월별 수익률"
                # "거래 패턴 분석"  # 거래내역 기능 비활성화로 제거
            ],
            key="analysis_chart_type"
        )
        
        # 차트별 옵션 설정
        if chart_type == "포트폴리오 성과":
            st.subheader("Portfolio Performance Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                days = st.slider("분석 기간 (일)", min_value=7, max_value=365, value=30)
            with col2:
                show_components = st.checkbox("구성 요소별 분석", value=True)
            
            if st.button("차트 생성", type="primary"):
                with st.spinner("포트폴리오 성과 차트를 생성하는 중..."):
                    chart_html = chart_service.create_portfolio_performance_chart(account_id, days=days)
                    
                    if chart_html:
                        st.components.v1.html(chart_html, height=600)
                    else:
                        st.warning("포트폴리오 성과 차트를 생성할 수 없습니다.")
        
        elif chart_type == "보유종목 비중":
            st.subheader("Holdings Weight Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                min_ratio = st.slider("최소 비중 (%)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
            with col2:
                show_others = st.checkbox("기타 종목 그룹화", value=True)
            
            if st.button("차트 생성", type="primary"):
                with st.spinner("보유종목 비중 차트를 생성하는 중..."):
                    chart_html = chart_service.create_holdings_pie_chart(account_id)
                    
                    if chart_html:
                        st.components.v1.html(chart_html, height=500)
                    else:
                        st.warning("보유종목 비중 차트를 생성할 수 없습니다.")
        
        elif chart_type == "보유종목 수익률":
            st.subheader("Holdings Return Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox("정렬 기준", ["수익률", "평가금액", "종목명"])
            with col2:
                show_benchmark = st.checkbox("벤치마크 표시", value=False)
            
            if st.button("차트 생성", type="primary"):
                with st.spinner("보유종목 수익률 차트를 생성하는 중..."):
                    chart_html = chart_service.create_holdings_performance_chart(account_id)
                    
                    if chart_html:
                        st.components.v1.html(chart_html, height=500)
                    else:
                        st.warning("보유종목 수익률 차트를 생성할 수 없습니다.")
        
        elif chart_type == "월별 수익률":
            st.subheader("Monthly Return Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                year = st.selectbox("분석 연도", range(2020, 2025), index=3)
            with col2:
                show_cumulative = st.checkbox("누적 수익률 표시", value=True)
            
            if st.button("차트 생성", type="primary"):
                with st.spinner("월별 수익률 차트를 생성하는 중..."):
                    chart_html = chart_service.create_monthly_return_chart(account_id, year)
                    
                    if chart_html:
                        st.components.v1.html(chart_html, height=500)
                    else:
                        st.warning("월별 수익률 차트를 생성할 수 없습니다.")
        
        # elif chart_type == "거래 패턴 분석":  # 거래내역 기능 비활성화
        #     st.subheader("Trading Pattern Analysis")
        #
        #     col1, col2 = st.columns(2)
        #     with col1:
        #         analysis_period = st.selectbox("분석 기간", ["최근 1개월", "최근 3개월", "최근 6개월", "최근 1년"])
        #     with col2:
        #         show_trend = st.checkbox("트렌드 라인 표시", value=True)
        #
        #     if st.button("차트 생성", type="primary"):
        #         with st.spinner("거래 패턴 차트를 생성하는 중..."):
        #             # 거래 패턴 분석 차트 생성 (추후 구현)
        #             st.info("거래 패턴 분석 기능은 추후 구현 예정입니다.")
        
        # 차트 설명
        st.subheader("Chart Explanation")
        
        if chart_type == "포트폴리오 성과":
            st.info("""
            **포트폴리오 성과 차트**는 시간에 따른 총 자산 변화와 수익률을 보여줍니다.
            - 상단 차트: 총 자산, 평가금액, 현금잔고 변화
            - 하단 차트: 일자별 수익률 변화
            """)
        
        elif chart_type == "보유종목 비중":
            st.info("""
            **보유종목 비중 차트**는 포트폴리오 내 각 종목의 비중을 시각화합니다.
            - 각 종목의 평가금액 비율을 파이 차트로 표시
            - 포트폴리오 집중도를 파악할 수 있습니다
            """)
        
        elif chart_type == "보유종목 수익률":
            st.info("""
            **보유종목 수익률 차트**는 각 종목의 수익률을 막대 차트로 보여줍니다.
            - 수익 종목은 녹색, 손실 종목은 빨간색으로 표시
            - 종목별 성과를 한눈에 비교할 수 있습니다
            """)
        
        elif chart_type == "월별 수익률":
            st.info("""
            **월별 수익률 차트**는 월별 포트폴리오 성과를 분석합니다.
            - 월별 총 자산 변화와 수익률을 동시에 표시
            - 계절성이나 특정 월의 성과 패턴을 파악할 수 있습니다
            """)
        
        # elif chart_type == "거래 패턴 분석":  # 거래내역 기능 비활성화
        #     st.info("""
        #     **거래 패턴 분석**은 거래 빈도와 패턴을 분석합니다.
        #     - 일별 거래량 변화
        #     - 매수/매도 비율
        #     - 거래 금액 분포
        #     """)
    
    except Exception as e:
        st.error(f"분석 차트를 생성하는 중 오류가 발생했습니다: {str(e)}")
        st.info("Tip: Please check database connection or try again later.")

if __name__ == "__main__":
    main()