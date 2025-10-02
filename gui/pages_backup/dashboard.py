"""
대시보드 페이지
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from gui.utils.data_service import DataService
from gui.utils.chart_service import ChartService

def show_welcome_dashboard():
    """계좌 선택이 안된 상태에서의 웰컴 대시보드"""

    # 메인 제목과 설명
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #1f77b4; margin-bottom: 1rem;'>📈 Stock Analyzer에 오신 것을 환영합니다!</h1>
        <p style='font-size: 1.2rem; color: #666; margin-bottom: 2rem;'>
            한국투자증권 등 주요 증권사와 연동하여 포트폴리오를 분석하는 통합 플랫폼입니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 기능 소개 섹션
    st.markdown("## 🚀 주요 기능")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 📊 실시간 포트폴리오 분석
        - 실시간 잔고 조회
        - 수익률 분석
        - 위험도 평가
        - 자산 배분 현황
        """)

    with col2:
        st.markdown("""
        ### 📈 시각화 차트
        - 포트폴리오 성과 추이
        - 종목별 비중 분석
        - 수익률 비교 차트
        - 자산 분배 분석
        """)

    with col3:
        st.markdown("""
        ### 💼 투자 관리
        - 보유종목 관리
        - 포트폴리오 분석
        - 성과 추적
        - 리스크 관리
        """)

    # 시작하기 안내
    st.markdown("---")
    st.markdown("## 📋 시작하기")

    # 단계별 안내
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("""
        ### 1️⃣ 계좌 선택
        왼쪽 사이드바에서 분석할 계좌를 선택해주세요.

        ### 2️⃣ 데이터 확인
        선택한 계좌의 데이터를 실시간으로 확인하세요.

        ### 3️⃣ 분석 시작
        다양한 차트와 지표로 포트폴리오를 분석하세요.
        """)

    with col2:
        # 계좌 등록 상태 확인
        try:
            data_service = DataService()
            accounts_data = data_service.get_accounts()

            if accounts_data:
                st.success(f"✅ **{len(accounts_data)}개의 계좌**가 등록되어 있습니다!")

                # 등록된 계좌 목록 표시
                st.markdown("### 📋 등록된 계좌 목록")
                for acc in accounts_data:
                    broker_icon = "🏦" if acc['broker_name'] == "KIS" else "🏛️"
                    st.markdown(f"{broker_icon} **{acc['broker_name']}** - {acc['account_number']}")

                st.markdown("👈 **사이드바에서 계좌를 선택**하여 분석을 시작하세요!")

            else:
                st.warning("⚠️ 등록된 계좌가 없습니다.")
                st.markdown("""
                ### 📝 계좌 등록 방법
                1. 메인 콘솔 애플리케이션(`main.py`)을 실행
                2. API 키 설정 후 계좌 등록
                3. 웹 인터페이스에서 데이터 확인

                자세한 설정 방법은 `README.md`를 참고하세요.
                """)

        except Exception as e:
            st.error(f"계좌 정보를 불러오는 중 오류가 발생했습니다: {str(e)}")

    # 추가 정보 섹션
    st.markdown("---")
    st.markdown("## 💡 도움말")

    with st.expander("❓ 자주 묻는 질문"):
        st.markdown("""
        **Q: 어떤 증권사를 지원하나요?**
        A: 현재 한국투자증권(KIS)을 지원하며, 향후 다른 증권사도 추가될 예정입니다.

        **Q: 실시간 데이터인가요?**
        A: 네, 증권사 API를 통해 실시간 데이터를 제공합니다.

        **Q: 데이터는 어디에 저장되나요?**
        A: 로컬 SQLite 데이터베이스에 안전하게 저장됩니다.

        **Q: 보안은 어떻게 관리하나요?**
        A: API 키는 환경변수로 관리되며, 토큰은 암호화되어 저장됩니다.
        """)

    with st.expander("🔧 기술 스택"):
        st.markdown("""
        - **Backend**: Python, SQLAlchemy, FastAPI
        - **Frontend**: Streamlit, Plotly
        - **Database**: SQLite
        - **API**: 한국투자증권 OpenAPI
        - **Charts**: Plotly.js, Chart.js
        """)

    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.9rem;'>
        <p>Stock Analyzer v1.0 | 포트폴리오 분석 및 관리 플랫폼</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """대시보드 페이지"""
    st.title("Dashboard")

    # 계좌 ID 확인 (다중 선택 지원)
    selected_account_ids = st.session_state.get('selected_account_ids', [])

    if not selected_account_ids:
        show_welcome_dashboard()
        return

    # 현재는 첫 번째 선택된 계좌를 사용 (추후 다중 계좌 통합 기능 추가 예정)
    account_id = selected_account_ids[0]

    if len(selected_account_ids) > 1:
        st.info(f"Note: Showing data for the first selected account ({account_id}). Integrated analysis feature will be updated later.")

    # 데이터 서비스 초기화
    data_service = DataService()
    chart_service = ChartService()

    # 전체 활성 계좌의 당일 데이터 확인 및 자동 조회
    if data_service.has_any_missing_today_data():
        missing_data_status = data_service.check_all_accounts_today_data()
        missing_accounts = [acc_id for acc_id, has_data in missing_data_status.items() if not has_data]

        if missing_accounts:
            st.warning(f"⚠️ {len(missing_accounts)}개 활성 계좌의 오늘 날짜 데이터가 없습니다. 자동으로 전체 계좌 정보를 조회합니다.")

            # 자동 조회 실행 (session_state를 이용해 하루에 한 번만 실행)
            auto_collect_key = f"auto_collect_all_{date.today().strftime('%Y%m%d')}"

            if auto_collect_key not in st.session_state:
                try:
                    with st.spinner("모든 활성 계좌 정보를 자동 조회하는 중..."):
                        # DataService를 통해 전체 활성 계좌 데이터 수집 실행
                        collection_result = data_service.collect_all_active_accounts_data()

                        # 결과 처리
                        if collection_result['success']:
                            st.success(collection_result['message'])

                            # 실패한 계좌가 있는 경우 상세 정보 표시
                            if collection_result['failed_accounts']:
                                with st.expander("⚠️ 데이터 수집에 실패한 계좌", expanded=False):
                                    for failed in collection_result['failed_accounts']:
                                        st.error(f"• {failed['broker_name']} - {failed['account_number']}: {failed['error']}")

                            st.session_state[auto_collect_key] = True
                            st.rerun()  # 페이지 새로고침
                        else:
                            st.error(collection_result['message'])
                            st.info("💡 수동으로 '계좌 전체 정보 조회' 버튼을 클릭해주세요.")
                            st.session_state[auto_collect_key] = False

                except Exception as e:
                    st.error(f"❌ 자동 조회 중 오류가 발생했습니다: {str(e)}")
                    st.info("💡 수동으로 '계좌 전체 정보 조회' 버튼을 클릭해주세요.")

                    # 에러 발생 시에도 키를 설정하여 반복 실행 방지
                    st.session_state[auto_collect_key] = False
    
    try:
        # 로딩 표시
        with st.spinner("데이터를 불러오는 중..."):
            # 최신 잔고 정보 조회
            latest_balance = data_service.get_latest_balance(account_id)
            
            # 보유종목 정보 조회
            holdings_data = data_service.get_holdings(account_id)
            
            # 최근 거래내역 조회 (최근 10건) - 비활성화
            # recent_transactions = data_service.get_recent_transactions(account_id, limit=10)
            recent_transactions = []  # 거래내역 기능 비활성화
        
        # 주요 지표 카드
        st.subheader("Key Metrics")
        
        if latest_balance:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "총 자산",
                    f"{latest_balance['total_balance']:,.0f}원",
                    f"{latest_balance['profit_loss_rate']:.2f}%"
                )
            
            with col2:
                st.metric(
                    "현금잔고",
                    f"{latest_balance['cash_balance']:,.0f}원",
                    f"비중 {(latest_balance['cash_balance']/latest_balance['total_balance']*100):.1f}%"
                )

            with col3:
                st.metric(
                    "주식잔고",
                    f"{latest_balance['stock_balance']:,.0f}원",
                    f"+{latest_balance['profit_loss_rate']:.2f}%" if latest_balance['profit_loss_rate'] >= 0 else f"{latest_balance['profit_loss_rate']:.2f}%"
                )
            
            with col4:
                st.metric(
                    "보유종목",
                    f"{len(holdings_data)}개",
                    f"{sum(1 for h in holdings_data if h['profit_loss_rate'] > 0)}개 수익"
                )
        else:
            st.warning("잔고 정보를 불러올 수 없습니다.")
        
        # 차트 섹션 제거 - Analysis 페이지에서 상세 분석 제공
        # st.subheader("Portfolio Performance")
        #
        # # 차트 타입 선택
        # chart_type = st.radio(
        #     "차트 타입 선택",
        #     ["포트폴리오 성과", "보유종목 비중", "보유종목 수익률"],
        #     horizontal=True
        # )
        #
        # if chart_type == "포트폴리오 성과":
        #     # 포트폴리오 성과 차트
        #     chart_html = chart_service.create_portfolio_performance_chart(account_id, days=30)
        #     if chart_html:
        #         st.components.v1.html(chart_html, height=600)
        #     else:
        #         st.warning("포트폴리오 성과 차트를 생성할 수 없습니다.")
        #
        # elif chart_type == "보유종목 비중":
        #     # 보유종목 비중 파이 차트
        #     chart_html = chart_service.create_holdings_pie_chart(account_id)
        #     if chart_html:
        #         st.components.v1.html(chart_html, height=500)
        #     else:
        #         st.warning("보유종목 비중 차트를 생성할 수 없습니다.")
        #
        # elif chart_type == "보유종목 수익률":
        #     # 보유종목 수익률 차트
        #     chart_html = chart_service.create_holdings_performance_chart(account_id)
        #     if chart_html:
        #         st.components.v1.html(chart_html, height=500)
        #     else:
        #         st.warning("보유종목 수익률 차트를 생성할 수 없습니다.")

        # Analysis 페이지 안내
        st.subheader("📊 상세 분석")
        st.info("""
        **더 자세한 분석이 필요하신가요?**

        📈 **Analysis 페이지**에서 다양한 차트와 분석 도구를 확인하세요:
        - 포트폴리오 성과 추이 분석
        - 보유종목 비중 및 수익률 차트
        - 월별 수익률 분석
        - 맞춤형 기간 설정 분석

        👈 사이드바에서 **Analysis**를 선택하여 이동하세요!
        """)
        
        # 최근 거래내역 - 비활성화
        # st.subheader("Recent Transactions")
        #
        # if recent_transactions:
        #     # DataFrame 생성
        #     df = pd.DataFrame(recent_transactions)
        #     df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        #     df = df.sort_values('transaction_date', ascending=False)
        #
        #     # 컬럼 포맷팅
        #     df['price'] = df['price'].apply(lambda x: f"{x:,.0f}원")
        #     df['amount'] = df['amount'].apply(lambda x: f"{x:,.0f}원")
        #     df['fee'] = df['fee'].apply(lambda x: f"{x:,.0f}원")
        #
        #     # 거래 유형별 색상
        #     def color_transaction_type(val):
        #         if val == 'BUY':
        #             return 'background-color: lightblue'
        #         elif val == 'SELL':
        #             return 'background-color: lightcoral'
        #         return ''
        #
        #     # 테이블 표시
        #     styled_df = df.style.applymap(color_transaction_type, subset=['transaction_type'])
        #     st.dataframe(
        #         styled_df,
        #         use_container_width=True,
        #         hide_index=True,
        #         column_config={
        #             "transaction_date": "거래일",
        #             "symbol": "종목코드",
        #             "name": "종목명",
        #             "transaction_type": "구분",
        #             "quantity": "수량",
        #             "price": "단가",
        #             "amount": "거래금액",
        #             "fee": "수수료"
        #         }
        #     )
        # else:
        #     st.info("최근 거래내역이 없습니다.")
        
        # 새로고침 버튼 제거 - 차트가 없으므로 불필요
        # col1, col2, col3 = st.columns([1, 1, 1])
        # with col2:
        #     if st.button("Refresh Data", type="primary"):
        #         st.rerun()
    
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")
        st.info("Tip: Please check database connection or try again later.")

if __name__ == "__main__":
    main()