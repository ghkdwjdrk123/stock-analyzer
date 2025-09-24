"""
한국투자증권 API 연동 클래스
"""
import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.brokers.base_broker import BaseBroker
from app.utils.exceptions import BrokerError, AuthenticationError
from app.utils.logger import get_logger
from app.utils.token_manager import TokenManager

logger = get_logger(__name__)

class KISBroker(BaseBroker):
    """한국투자증권 API 연동 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_settings = config.get('api_settings', {})
        self.credentials = config.get('credentials', {})
        self.base_url = self.api_settings.get('base_url', 'https://openapi.koreainvestment.com:9443')
        self.timeout = self.api_settings.get('timeout', 30)
        self.retry_count = self.api_settings.get('retry_count', 3)
        self.rate_limit = self.api_settings.get('rate_limit', {})
        self.token_refresh_threshold = self.api_settings.get('token_refresh_threshold', 300)
        
        # API 설정 (환경변수에서 로드)
        self.tr_id_balance = self.api_settings.get('tr_id_balance', 'TTTC8434R')
        self.account_product_code = self.api_settings.get('account_product_code', '01')
        self.market_div_code = self.api_settings.get('market_div_code', 'J')
        
        # API 엔드포인트 (환경변수에서 로드)
        self.api_balance = self.api_settings.get('api_balance', '/uapi/domestic-stock/v1/trading/inquire-balance')
        self.api_accounts = self.api_settings.get('api_accounts', '/uapi/domestic-stock/v1/trading/inquire-balance')
        
        # 계좌 정보 (환경변수에서 로드)
        self.account_8_prod = self.api_settings.get('account_8_prod')
        self.account_pd_prod = self.api_settings.get('account_pd_prod')
        
        # API 인증 정보
        self.app_key = self.credentials.get('app_key')
        self.app_secret = self.credentials.get('app_secret')
        
        # 디버깅용 로그
        logger.debug(f"KIS API 설정 - app_key: {self.app_key[:10] + '...' if self.app_key else 'None'}")
        logger.debug(f"KIS API 설정 - app_secret: {'설정됨' if self.app_secret else 'None'}")
        
        # 토큰 관리자 초기화 (증권사별)
        self.token_manager = TokenManager(broker_name="kis")
        self.access_token = None
        self.refresh_token = None
        
        # 세션 설정
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json; charset=utf-8'
        })
    
    def connect(self) -> bool:
        """한국투자증권 API 연결"""
        try:
            logger.info(f"{self.name} API 연결을 시작합니다.")
            
            # 앱 키와 시크릿 확인
            if not self.app_key or not self.app_secret:
                raise AuthenticationError("앱 키 또는 앱 시크릿이 설정되지 않았습니다.")
            
            # 토큰 확인 및 발급/갱신
            if not self._load_or_refresh_token():
                self._get_access_token()
            
            self.connected = True
            logger.info(f"{self.name} API 연결이 완료되었습니다.")
            return True
            
        except Exception as e:
            logger.error(f"{self.name} API 연결 실패: {str(e)}")
            self.connected = False
            raise BrokerError(f"API 연결 실패: {str(e)}")
    
    def disconnect(self) -> bool:
        """한국투자증권 API 연결 해제"""
        try:
            self.session.close()
            self.connected = False
            logger.info(f"{self.name} API 연결이 해제되었습니다.")
            return True
        except Exception as e:
            logger.error(f"{self.name} API 연결 해제 실패: {str(e)}")
            return False
    
    def _load_or_refresh_token(self) -> bool:
        """저장된 토큰 로드 또는 갱신"""
        try:
            # 저장된 토큰 확인
            if self.token_manager.is_token_valid():
                self.access_token = self.token_manager.get_access_token()
                self.refresh_token = self.token_manager.get_refresh_token()
                logger.info(f"저장된 토큰을 사용합니다: {self.name}")
                return True
            
            # 토큰이 만료되었거나 없으면 새로 발급
            logger.info(f"토큰이 만료되었거나 없습니다. 새로 발급합니다: {self.name}")
            return False
            
        except Exception as e:
            logger.error(f"토큰 로드 실패: {str(e)}")
            return False
    
    def _get_access_token(self) -> str:
        """액세스 토큰 발급"""
        try:
            url = f"{self.base_url}/oauth2/tokenP"
            data = {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 86400)
            
            # 토큰을 파일에 저장
            self.token_manager.save_token(
                access_token=self.access_token,
                refresh_token=self.refresh_token,
                expires_in=expires_in
            )
            
            logger.info("액세스 토큰이 발급되고 저장되었습니다.")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"토큰 발급 실패: {str(e)}")
    
    def _is_token_expired(self) -> bool:
        """토큰 만료 여부 확인"""
        return not self.token_manager.is_token_valid()
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """API 요청 실행 (재시도 로직 포함)"""
        for attempt in range(self.retry_count):
            try:
                # 토큰 갱신 확인
                if self._is_token_expired():
                    self._get_access_token()
                
                # 헤더 설정
                headers = kwargs.get('headers', {})
                headers.update({
                    'authorization': f'Bearer {self.access_token}',
                    'appkey': self.app_key,
                    'appsecret': self.app_secret
                })
                kwargs['headers'] = headers
                
                # 요청 실행
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                
                # Rate limiting
                if self.rate_limit.get('requests_per_second'):
                    time.sleep(1.0 / self.rate_limit['requests_per_second'])
                
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_count - 1:
                    raise BrokerError(f"API 요청 실패: {str(e)}")
                
                # 재시도 전 대기
                time.sleep(2 ** attempt)
        
        raise BrokerError("최대 재시도 횟수 초과")
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """계좌 목록 조회"""
        try:
            if not self.connected:
                self.connect()
            
            # 환경변수에서 계좌 정보가 있으면 사용
            if self.account_8_prod and self.account_pd_prod:
                accounts = [{
                    'account_number': f"{self.account_8_prod}{self.account_pd_prod}",
                    'account_name': '한국투자증권 계좌',
                    'account_type': '일반',
                    'broker_name': '한국투자증권'
                }]
                logger.info(f"환경변수에서 계좌 정보를 로드했습니다: {accounts[0]['account_number']}")
            else:
                # TODO: 실제 계좌 조회 API 구현
                accounts = []
                logger.warning("계좌 정보가 환경변수에 설정되지 않았습니다.")
            
            logger.info(f"계좌 {len(accounts)}개를 조회했습니다.")
            return accounts
            
        except Exception as e:
            logger.error(f"계좌 목록 조회 실패: {str(e)}")
            raise BrokerError(f"계좌 목록 조회 실패: {str(e)}")
    
    def get_balance(self, account_number: str) -> Dict[str, Any]:
        """계좌 잔고 조회"""
        try:
            if not self.connected:
                self.connect()
            
            url = f"{self.base_url}{self.api_balance}"
            headers = {
                'authorization': f'Bearer {self.access_token}',
                'appkey': self.app_key,
                'appsecret': self.app_secret,
                'tr_id': self.tr_id_balance,
                'custtype': 'P'
            }
            params = {
                'CANO': account_number[:8],  # 계좌번호 앞 8자리
                'ACNT_PRDT_CD': self.account_product_code,
                'AFHR_FLPR_YN': 'N',
                'OFL_YN': 'N',  # 실전거래
                'INQR_DVSN': '01',  # 체결기준
                'UNPR_DVSN': '01',  # 현재가 기준
                'FUND_STTL_ICLD_YN': 'N',
                'FNCG_AMT_AUTO_RDPT_YN': 'N',
                'PRCS_DVSN': '01',
                'CTX_AREA_FK100': '',
                'CTX_AREA_NK100': ''
            }
            
            # 계좌번호 처리 (환경변수에서 가져온 계좌 정보 사용)
            if self.account_8_prod and self.account_pd_prod:
                cano = self.account_8_prod  # 앞 8자리
                acnt_prdt_cd = self.account_pd_prod  # 계좌상품코드
            else:
                cano = account_number[:8]  # 계좌번호 앞 8자리
                acnt_prdt_cd = self.account_product_code
            
            params = {
                'CANO': cano,
                'ACNT_PRDT_CD': acnt_prdt_cd,
                'AFHR_FLPR_YN': 'N',
                'OFL_YN': 'N',  # 실전거래
                'INQR_DVSN': '01',  # 체결기준
                'UNPR_DVSN': '01',  # 현재가 기준
                'FUND_STTL_ICLD_YN': 'N',
                'FNCG_AMT_AUTO_RDPT_YN': 'N',
                'PRCS_DVSN': '01',
                'CTX_AREA_FK100': '',
                'CTX_AREA_NK100': ''
            }
            
            response = self._make_request('GET', url, headers=headers, params=params)
            data = response.json()
            
            # 잔고 정보 파싱 (사용자 제공 API 명세에 맞게)
            balance_info = {
                'account_number': account_number,
                'cash_balance': 0,
                'stock_balance': 0,
                'total_balance': 0,
                'evaluation_amount': 0,
                'profit_loss': 0,
                'profit_loss_rate': 0.0
            }
            
            # output2에서 계좌 요약 정보 추출
            if 'output2' in data:
                output2 = data['output2']
                if isinstance(output2, dict):
                    balance_info['cash_balance'] = float(output2.get('dnca_tot_amt', 0))  # 총예수금
                    balance_info['total_balance'] = float(output2.get('tot_asst_amt', 0))  # 총자산
                    balance_info['evaluation_amount'] = float(output2.get('evlu_amt', 0))  # 평가금액
                    balance_info['profit_loss'] = float(output2.get('evlu_pfls_amt', 0))  # 평가손익
                    balance_info['profit_loss_rate'] = float(output2.get('evlu_pfls_rt', 0))  # 평가손익률
                    
                    # 주식 잔고 = 총자산 - 현금잔고
                    balance_info['stock_balance'] = balance_info['total_balance'] - balance_info['cash_balance']
                elif isinstance(output2, list) and len(output2) > 0:
                    # 리스트 형태인 경우 첫 번째 항목 사용
                    output2_item = output2[0]
                    balance_info['cash_balance'] = float(output2_item.get('dnca_tot_amt', 0))  # 총예수금
                    balance_info['total_balance'] = float(output2_item.get('tot_asst_amt', 0))  # 총자산
                    balance_info['evaluation_amount'] = float(output2_item.get('evlu_amt', 0))  # 평가금액
                    balance_info['profit_loss'] = float(output2_item.get('evlu_pfls_amt', 0))  # 평가손익
                    balance_info['profit_loss_rate'] = float(output2_item.get('evlu_pfls_rt', 0))  # 평가손익률
                    
                    # 주식 잔고 = 총자산 - 현금잔고
                    balance_info['stock_balance'] = balance_info['total_balance'] - balance_info['cash_balance']
            
            logger.info(f"계좌 {account_number} 잔고 조회 완료")
            return balance_info
            
        except Exception as e:
            logger.error(f"계좌 {account_number} 잔고 조회 실패: {str(e)}")
            raise BrokerError(f"잔고 조회 실패: {str(e)}")
    
    def get_holdings(self, account_number: str) -> List[Dict[str, Any]]:
        """보유종목 조회"""
        try:
            if not self.connected:
                self.connect()
            
            url = f"{self.base_url}{self.api_balance}"
            headers = {
                'authorization': f'Bearer {self.access_token}',
                'appkey': self.app_key,
                'appsecret': self.app_secret,
                'tr_id': self.tr_id_balance,
                'custtype': 'P'
            }
            
            # 계좌번호 처리 (환경변수에서 가져온 계좌 정보 사용)
            if self.account_8_prod and self.account_pd_prod:
                cano = self.account_8_prod  # 앞 8자리
                acnt_prdt_cd = self.account_pd_prod  # 계좌상품코드
            else:
                cano = account_number[:8]  # 계좌번호 앞 8자리
                acnt_prdt_cd = self.account_product_code
            
            params = {
                'CANO': cano,
                'ACNT_PRDT_CD': acnt_prdt_cd,
                'AFHR_FLPR_YN': 'N',
                'OFL_YN': 'N',  # 실전거래
                'INQR_DVSN': '01',  # 체결기준
                'UNPR_DVSN': '01',  # 현재가 기준
                'FUND_STTL_ICLD_YN': 'N',
                'FNCG_AMT_AUTO_RDPT_YN': 'N',
                'PRCS_DVSN': '01',
                'CTX_AREA_FK100': '',
                'CTX_AREA_NK100': ''
            }
            
            response = self._make_request('GET', url, headers=headers, params=params)
            data = response.json()
            
            holdings = []
            if 'output1' in data:
                for item in data['output1']:
                    if item.get('pdno'):  # 주식 종목
                        holdings.append({
                            'symbol': item.get('pdno', ''),  # 종목코드
                            'name': item.get('prdt_name', ''),  # 종목명
                            'quantity': int(item.get('hldg_qty', 0)),  # 보유수량
                            'average_price': float(item.get('pchs_avg_pric', 0)),  # 평균단가
                            'current_price': float(item.get('prpr', 0)),  # 현재가
                            'evaluation_amount': float(item.get('evlu_amt', 0)),  # 평가금액
                            'profit_loss': float(item.get('evlu_pfls_amt', 0)),  # 평가손익
                            'profit_loss_rate': float(item.get('evlu_pfls_rt', 0))  # 평가손익률
                        })
            
            logger.info(f"계좌 {account_number} 보유종목 {len(holdings)}개 조회 완료")
            return holdings
            
        except Exception as e:
            logger.error(f"계좌 {account_number} 보유종목 조회 실패: {str(e)}")
            raise BrokerError(f"보유종목 조회 실패: {str(e)}")
    
    def get_transactions(self, account_number: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """거래내역 조회"""
        try:
            if not self.connected:
                self.connect()
            
            # 거래내역 조회 API (실제 구현 시 적절한 API 엔드포인트 사용)
            url = f"{self.base_url}{self.api_balance}"
            headers = {
                'tr_id': 'TTTC8434R',
                'custtype': 'P'
            }
            
            # 날짜 형식 변환
            start_date_str = start_date.strftime('%Y%m%d')
            end_date_str = end_date.strftime('%Y%m%d')
            
            params = {
                'CANO': account_number,
                'ACNT_PRDT_CD': '01',
                'AFHR_FLPR_YN': 'N',
                'OFL_YN': '',
                'INQR_DVSN': '01',
                'UNPR_DVSN': '01',
                'FUND_STTL_ICLD_YN': 'N',
                'FNCG_AMT_AUTO_RDPT_YN': 'N',
                'PRCS_DVSN': '01',
                'CTX_AREA_FK100': '',
                'CTX_AREA_NK100': ''
            }
            
            response = self._make_request('GET', url, headers=headers, params=params)
            data = response.json()
            
            # 거래내역 파싱 (실제 구현 시 적절한 파싱 로직 필요)
            transactions = []
            # TODO: 실제 거래내역 조회 API 구현
            
            logger.info(f"계좌 {account_number} 거래내역 조회 완료")
            return transactions
            
        except Exception as e:
            logger.error(f"계좌 {account_number} 거래내역 조회 실패: {str(e)}")
            raise BrokerError(f"거래내역 조회 실패: {str(e)}")
    
    def get_stock_price(self, stock_code: str) -> Dict[str, Any]:
        """종목 가격 조회 (보유종목 조회 API 사용) - 보유종목만 조회 가능"""
        try:
            if not self.connected:
                self.connect()
            
            # 보유종목 조회를 통해 해당 종목 정보 찾기
            if not self.account_8_prod or not self.account_pd_prod:
                raise BrokerError("계좌 정보가 설정되지 않았습니다.")
            
            # 보유종목 조회
            holdings = self.get_holdings(f"{self.account_8_prod}{self.account_pd_prod}")
            
            # 해당 종목 찾기
            for holding in holdings:
                if holding.get('symbol') == stock_code:
                    return {
                        'stock_code': stock_code,
                        'stock_name': holding.get('name', ''),
                        'current_price': holding.get('current_price', 0),
                        'change_rate': holding.get('profit_loss_rate', 0),
                        'change_price': holding.get('current_price', 0) - holding.get('average_price', 0),
                        'quantity': holding.get('quantity', 0),
                        'evaluation_amount': holding.get('evaluation_amount', 0),
                        'profit_loss': holding.get('profit_loss', 0)
                    }
            
            # 보유하지 않은 종목인 경우
            raise BrokerError(f"보유하지 않은 종목입니다: {stock_code}")
                
        except Exception as e:
            logger.error(f"종목 가격 조회 실패: {str(e)}")
            raise BrokerError(f"종목 가격 조회 실패: {str(e)}")
