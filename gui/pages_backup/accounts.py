"""
계좌 관리 페이지
"""
import streamlit as st
import pandas as pd
from gui.utils.data_service import DataService

def main():
    """계좌 관리 페이지"""
    st.title("Account Management")
    
    # 데이터 서비스 초기화
    data_service = DataService()
    
    try:
        # 계좌 목록 조회
        with st.spinner("계좌 정보를 불러오는 중..."):
            accounts_data = data_service.get_accounts()
        
        if accounts_data:
            st.subheader("Registered Accounts")
            
            # DataFrame 생성
            df = pd.DataFrame(accounts_data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at', ascending=False)
            
            # 컬럼 포맷팅
            df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
            
            # 테이블 표시
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "broker_name": "증권사",
                    "account_number": "계좌번호",
                    "account_name": "계좌명",
                    "account_type": "계좌유형",
                    "is_active": "활성상태",
                    "created_at": "등록일"
                }
            )
            
            # 계좌별 상세 정보
            st.subheader("Account Details")
            
            selected_account_id = st.selectbox(
                "상세 정보를 확인할 계좌를 선택하세요",
                [f"{acc['broker_name']} - {acc['account_number']}" for acc in accounts_data],
                key="account_detail_selector"
            )
            
            if selected_account_id:
                # 선택된 계좌의 ID 찾기
                selected_account = None
                for acc in accounts_data:
                    if f"{acc['broker_name']} - {acc['account_number']}" == selected_account_id:
                        selected_account = acc
                        break
                
                if selected_account:
                    # 계좌 상세 정보 표시
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 계좌 기본 정보")
                        st.write(f"**증권사:** {selected_account['broker_name']}")
                        st.write(f"**계좌번호:** {selected_account['account_number']}")
                        st.write(f"**계좌명:** {selected_account['account_name'] or 'N/A'}")
                        st.write(f"**계좌유형:** {selected_account['account_type']}")
                        st.write(f"**활성상태:** {'활성' if selected_account['is_active'] else '비활성'}")
                        st.write(f"**등록일:** {selected_account['created_at']}")
                    
                    with col2:
                        st.markdown("### 최신 잔고 정보")
                        try:
                            latest_balance = data_service.get_latest_balance(selected_account['id'])
                            if latest_balance:
                                st.metric("총 자산", f"{latest_balance['total_balance']:,.0f}원")
                                st.metric("현금잔고", f"{latest_balance['cash_balance']:,.0f}원")
                                st.metric("주식잔고", f"{latest_balance['stock_balance']:,.0f}원")
                                st.metric("손익률", f"{latest_balance['profit_loss_rate']:.2f}%")
                            else:
                                st.warning("잔고 정보가 없습니다.")
                        except Exception as e:
                            st.error(f"잔고 정보를 불러올 수 없습니다: {str(e)}")
        else:
            st.warning("등록된 계좌가 없습니다.")
            st.info("Tip: Please register an account through the securities API.")
    
    except Exception as e:
        st.error(f"계좌 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")
        st.info("Tip: Please check database connection or try again later.")

if __name__ == "__main__":
    main()