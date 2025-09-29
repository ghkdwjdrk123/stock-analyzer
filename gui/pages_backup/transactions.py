"""
거래내역 페이지
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from gui.utils.data_service import DataService

def main():
    """거래내역 페이지"""
    st.title("Transactions")
    
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
    
    try:
        # 필터 옵션
        st.subheader("Search Filters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 날짜 범위 선택
            end_date = st.date_input("종료일", value=date.today())
            start_date = st.date_input("시작일", value=end_date - timedelta(days=30))
        
        with col2:
            # 거래 유형 필터
            transaction_type = st.selectbox(
                "거래 유형",
                ["전체", "매수", "매도"],
                key="transaction_type_filter"
            )
        
        with col3:
            # 종목 필터
            symbol_filter = st.text_input(
                "종목코드/종목명",
                placeholder="종목코드 또는 종목명 입력",
                key="symbol_filter"
            )
        
        # 거래내역 조회
        with st.spinner("거래내역을 불러오는 중..."):
            # 필터 조건 구성
            filters = {
                'start_date': start_date,
                'end_date': end_date
            }
            
            if transaction_type != "전체":
                filters['transaction_type'] = transaction_type
            
            if symbol_filter:
                filters['symbol'] = symbol_filter
            
            transactions_data = data_service.get_transactions(account_id, **filters)
        
        if transactions_data:
            # DataFrame 생성
            df = pd.DataFrame(transactions_data)
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            df = df.sort_values('transaction_date', ascending=False)
            
            # 컬럼 포맷팅
            df['price'] = df['price'].apply(lambda x: f"{x:,.0f}원")
            df['amount'] = df['amount'].apply(lambda x: f"{x:,.0f}원")
            df['fee'] = df['fee'].apply(lambda x: f"{x:,.0f}원")
            
            # 거래 유형별 색상 설정
            def color_transaction_type(val):
                if val == 'BUY':
                    return 'background-color: lightblue'
                elif val == 'SELL':
                    return 'background-color: lightcoral'
                return ''
            
            # 테이블 표시
            st.subheader("Transaction List")
            styled_df = df.style.applymap(color_transaction_type, subset=['transaction_type'])
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "transaction_date": "거래일",
                    "symbol": "종목코드",
                    "name": "종목명",
                    "transaction_type": "구분",
                    "quantity": "수량",
                    "price": "단가",
                    "amount": "거래금액",
                    "fee": "수수료"
                }
            )
            
            # 요약 정보
            st.subheader("Transaction Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_transactions = len(transactions_data)
                st.metric("총 거래건수", f"{total_transactions}건")
            
            with col2:
                buy_transactions = [t for t in transactions_data if t['transaction_type'] == 'BUY']
                buy_amount = sum(t['amount'] for t in buy_transactions)
                st.metric("총 매수금액", f"{buy_amount:,.0f}원")
            
            with col3:
                sell_transactions = [t for t in transactions_data if t['transaction_type'] == 'SELL']
                sell_amount = sum(t['amount'] for t in sell_transactions)
                st.metric("총 매도금액", f"{sell_amount:,.0f}원")
            
            with col4:
                total_fees = sum(t['fee'] for t in transactions_data)
                st.metric("총 수수료", f"{total_fees:,.0f}원")
            
            # 거래 패턴 분석
            st.subheader("Trading Pattern Analysis")
            
            # 일별 거래량
            daily_trades = df.groupby(df['transaction_date'].dt.date).size().reset_index()
            daily_trades.columns = ['거래일', '거래건수']
            
            if len(daily_trades) > 1:
                st.line_chart(daily_trades.set_index('거래일'))
            
            # 거래 유형별 분포
            transaction_counts = df['transaction_type'].value_counts()
            if len(transaction_counts) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.bar_chart(transaction_counts)
                
                with col2:
                    # 거래금액 분포
                    amount_by_type = df.groupby('transaction_type')['amount'].sum()
                    st.bar_chart(amount_by_type)
            
            # 내보내기 기능
            st.subheader("Data Export")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Export CSV", type="primary"):
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="CSV 파일 다운로드",
                        data=csv,
                        file_name=f"transactions_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("Export Excel"):
                    # Excel 파일 생성 (pandas의 to_excel 사용)
                    excel_buffer = pd.ExcelWriter('temp_transactions.xlsx', engine='openpyxl')
                    df.to_excel(excel_buffer, index=False, sheet_name='거래내역')
                    excel_buffer.close()
                    
                    with open('temp_transactions.xlsx', 'rb') as f:
                        excel_data = f.read()
                    
                    st.download_button(
                        label="Excel 파일 다운로드",
                        data=excel_data,
                        file_name=f"transactions_{start_date}_{end_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        else:
            st.warning("해당 조건에 맞는 거래내역이 없습니다.")
            st.info("Tip: Try different date ranges or filter conditions.")
    
    except Exception as e:
        st.error(f"거래내역을 불러오는 중 오류가 발생했습니다: {str(e)}")
        st.info("Tip: Please check database connection or try again later.")

if __name__ == "__main__":
    main()