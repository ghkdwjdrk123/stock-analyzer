"""
Stock Analyzer GUI - 메인 애플리케이션
"""
import streamlit as st
import sys
from pathlib import Path
from streamlit_option_menu import option_menu

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.utils.data_service import DataService

def main():
    """메인 애플리케이션"""
    # 페이지 설정
    st.set_page_config(
        page_title="Stock Analyzer",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 사이드바 너비 고정을 위한 CSS 스타일
    st.markdown("""
    <style>
    .css-1d391kg {
        width: 330px !important;
        min-width: 330px !important;
        max-width: 330px !important;
    }
    .css-1cypcdb {
        width: 330px !important;
        min-width: 330px !important;
        max-width: 330px !important;
    }
    section[data-testid="stSidebar"] {
        width: 330px !important;
        min-width: 330px !important;
        max-width: 330px !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 330px !important;
        min-width: 330px !important;
        max-width: 330px !important;
    }
    .css-1lcbmhc {
        width: 330px !important;
        min-width: 330px !important;
        max-width: 330px !important;
    }
    .css-1outpf7 {
        width: 330px !important;
        min-width: 330px !important;
        max-width: 330px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 메인 헤더
    st.markdown('<h1 class="main-header">Stock Analyzer</h1>', unsafe_allow_html=True)
    
    # 사이드바 구성
    with st.sidebar:
        # 메뉴 선택
        selected_page = option_menu(
            "Stock Analyzer",
            ["Dashboard", "Accounts", "Holdings", "Transactions", "Analysis"],
            icons=['house', 'bank', 'graph-up', 'list-ul', 'bar-chart'],
            menu_icon="app-indicator",
            default_index=0,
            styles={
                "container": {"padding": "10!important", "background-color": "#2c3e50", "border-radius": "10px"},
                "icon": {"color": "#bdc3c7", "font-size": "22px"}, 
                "nav-link": {
                    "font-size": "18px", 
                    "text-align": "left", 
                    "margin": "2px", 
                    "color": "#bdc3c7",
                    "--hover-color": "#4a5f7a",
                    "border-radius": "5px"
                },
                "nav-link-selected": {
                    "background-color": "#1f77b4",
                    "color": "#ffffff",
                    "border-radius": "5px"
                },
            }
        )
        
        st.markdown("---")
        
        # 계좌 선택
        st.markdown("### Account Selection")
        try:
            data_service = DataService()
            accounts_data = data_service.get_accounts()

            if accounts_data:
                # 계좌 옵션을 '증권사 - 계좌번호' 형태로 생성
                account_options = {}
                for acc in accounts_data:
                    display_name = f"{acc['broker_name']} - {acc['account_number']}"
                    account_options[display_name] = acc['id']

                # 다중 선택 가능한 드롭다운
                selected_accounts = st.multiselect(
                    "계좌 선택",
                    list(account_options.keys()),
                    key="account_selector",
                    label_visibility="collapsed"
                )

                # 선택된 계좌 ID 리스트를 세션에 저장
                if selected_accounts:
                    selected_account_ids = [account_options[acc] for acc in selected_accounts]
                    st.session_state.selected_account_ids = selected_account_ids

                    # 선택된 계좌 리스트 표시
                    st.markdown("**Selected Accounts:**")
                    for acc_name in selected_accounts:
                        st.markdown(f"• {acc_name}")
                else:
                    st.session_state.selected_account_ids = []
            else:
                st.warning("No registered accounts found.")
                st.session_state.selected_account_ids = []

        except Exception as e:
            st.error(f"Cannot load account information: {str(e)}")
            st.session_state.selected_account_ids = []
        
        st.markdown("---")
        
        # 앱 정보
        st.markdown("### App Info")
        st.info("""
        **Stock Analyzer v1.0**
        
        Portfolio Analysis
        Real-time Data
        Transaction Management
        """)
    
    # 메인 컨텐츠 영역 - 선택된 페이지에 따라 표시
    if selected_page == "Dashboard":
        from gui.pages_backup import dashboard
        dashboard.main()
    elif selected_page == "Accounts":
        from gui.pages_backup import accounts
        accounts.main()
    elif selected_page == "Holdings":
        from gui.pages_backup import holdings
        holdings.main()
    elif selected_page == "Transactions":
        from gui.pages_backup import transactions
        transactions.main()
    elif selected_page == "Analysis":
        from gui.pages_backup import analysis
        analysis.main()

if __name__ == "__main__":
    main()