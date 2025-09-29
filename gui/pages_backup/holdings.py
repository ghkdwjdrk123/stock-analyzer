"""
보유종목 페이지
"""
import streamlit as st
import pandas as pd
from gui.utils.data_service import DataService
from gui.utils.chart_service import ChartService

def main():
    """보유종목 페이지"""
    st.title("Holdings")
    
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
        # 보유종목 데이터 조회
        with st.spinner("보유종목 정보를 불러오는 중..."):
            holdings_data = data_service.get_holdings(account_id)
        
        if holdings_data:
            # 필터 및 정렬 옵션
            st.subheader("Filter and Sort")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sort_by = st.selectbox(
                    "정렬 기준",
                    ["평가금액", "수익률", "종목명", "수량"],
                    key="holdings_sort"
                )
            
            with col2:
                filter_profit = st.selectbox(
                    "수익률 필터",
                    ["전체", "수익", "손실"],
                    key="holdings_profit_filter"
                )
            
            with col3:
                min_amount = st.number_input(
                    "최소 평가금액 (원)",
                    min_value=0,
                    value=0,
                    step=10000,
                    key="holdings_min_amount"
                )
            
            # 데이터 필터링 및 정렬
            filtered_data = holdings_data.copy()
            
            # 수익률 필터
            if filter_profit == "수익":
                filtered_data = [h for h in filtered_data if h['profit_loss_rate'] > 0]
            elif filter_profit == "손실":
                filtered_data = [h for h in filtered_data if h['profit_loss_rate'] < 0]
            
            # 최소 평가금액 필터
            if min_amount > 0:
                filtered_data = [h for h in filtered_data if h['evaluation_amount'] >= min_amount]
            
            # 정렬
            if sort_by == "평가금액":
                filtered_data.sort(key=lambda x: x['evaluation_amount'], reverse=True)
            elif sort_by == "수익률":
                filtered_data.sort(key=lambda x: x['profit_loss_rate'], reverse=True)
            elif sort_by == "종목명":
                filtered_data.sort(key=lambda x: x['name'])
            elif sort_by == "수량":
                filtered_data.sort(key=lambda x: x['quantity'], reverse=True)
            
            # 보유종목 테이블
            st.subheader("Holdings List")
            
            if filtered_data:
                # DataFrame 생성
                df = pd.DataFrame(filtered_data)
                
                # 컬럼 포맷팅
                df['average_price'] = df['average_price'].apply(lambda x: f"{x:,.0f}원")
                df['current_price'] = df['current_price'].apply(lambda x: f"{x:,.0f}원")
                df['evaluation_amount'] = df['evaluation_amount'].apply(lambda x: f"{x:,.0f}원")
                df['profit_loss'] = df['profit_loss'].apply(lambda x: f"{x:,.0f}원")
                df['profit_loss_rate'] = df['profit_loss_rate'].apply(lambda x: f"{x:.2f}%")
                
                # 수익률별 색상 설정
                def color_profit_loss(val):
                    if val.endswith('%'):
                        rate = float(val[:-1])
                        if rate > 0:
                            return 'background-color: lightgreen'
                        elif rate < 0:
                            return 'background-color: lightcoral'
                    return ''
                
                # 테이블 표시
                styled_df = df.style.applymap(color_profit_loss, subset=['profit_loss_rate'])
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "symbol": "종목코드",
                        "name": "종목명",
                        "quantity": "수량",
                        "average_price": "평균단가",
                        "current_price": "현재가",
                        "evaluation_amount": "평가금액",
                        "profit_loss": "손익",
                        "profit_loss_rate": "수익률"
                    }
                )
                
                # 요약 정보
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("총 보유종목", f"{len(filtered_data)}개")
                
                with col2:
                    total_evaluation = sum(h['evaluation_amount'] for h in filtered_data)
                    st.metric("총 평가금액", f"{total_evaluation:,.0f}원")
                
                with col3:
                    profit_count = sum(1 for h in filtered_data if h['profit_loss_rate'] > 0)
                    st.metric("수익 종목", f"{profit_count}개")
                
                with col4:
                    total_profit = sum(h['profit_loss'] for h in filtered_data)
                    st.metric("총 손익", f"{total_profit:,.0f}원")
                
            else:
                st.warning("필터 조건에 맞는 보유종목이 없습니다.")
            
            # 차트 섹션
            st.subheader("Chart Analysis")
            
            chart_type = st.radio(
                "차트 타입 선택",
                ["보유종목 비중", "보유종목 수익률"],
                horizontal=True,
                key="holdings_chart_type"
            )
            
            if chart_type == "보유종목 비중":
                # 보유종목 비중 파이 차트
                chart_html = chart_service.create_holdings_pie_chart(account_id)
                if chart_html:
                    st.components.v1.html(chart_html, height=500)
                else:
                    st.warning("보유종목 비중 차트를 생성할 수 없습니다.")
            
            elif chart_type == "보유종목 수익률":
                # 보유종목 수익률 차트
                chart_html = chart_service.create_holdings_performance_chart(account_id)
                if chart_html:
                    st.components.v1.html(chart_html, height=500)
                else:
                    st.warning("보유종목 수익률 차트를 생성할 수 없습니다.")
        
        else:
            st.warning("보유종목이 없습니다.")
            st.info("Tip: Holdings will appear here after making trades.")
    
    except Exception as e:
        st.error(f"보유종목 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")
        st.info("Tip: Please check database connection or try again later.")

if __name__ == "__main__":
    main()