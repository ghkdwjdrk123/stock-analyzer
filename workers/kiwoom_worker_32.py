"""
키움증권 32비트 Worker 프로세스
64비트 메인 프로그램에서 subprocess로 실행되는 32비트 전용 스크립트

Usage:
    python kiwoom_worker_32.py <command> [args...]

Commands:
    get_accounts - 계좌 목록 조회
    get_balance <account_number> - 계좌 잔고 조회
    get_holdings <account_number> - 보유종목 조회
"""

import sys
import json
import os
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QApplication
from queue import Queue, Empty
import time


class KiwoomWorker:
    """키움 API 32비트 워커"""

    def __init__(self):
        self.kiwoom = None
        self.connected = False
        self.account_list = []
        self.request_queue = {}

        # 환경변수 로드
        from dotenv import load_dotenv
        load_dotenv('env')

        self.account_password = os.getenv('KIWOOM_ACCOUNT_PASSWORD', '')
        self.delisted_filter = os.getenv('KIWOOM_DELISTED_FILTER', '0')
        self.password_media = os.getenv('KIWOOM_PASSWORD_MEDIA', '00')
        self.exchange_code = os.getenv('KIWOOM_EXCHANGE_CODE', 'KRX')
        self.tr_balance = os.getenv('KIWOOM_TR_BALANCE', 'opw00018')
        self.tr_holdings = os.getenv('KIWOOM_TR_HOLDINGS', 'OPW00004')

    def initialize(self):
        """키움 API 초기화"""
        try:
            # QAxWidget 생성 (위키독스 방식)
            self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

            # 이벤트 핸들러 연결
            self.kiwoom.OnEventConnect.connect(self._on_event_connect)
            self.kiwoom.OnReceiveTrData.connect(self._on_receive_tr_data)

            return True
        except Exception as e:
            self._error_exit(f"키움 API 초기화 실패: {str(e)}")

    def login(self, timeout=30):
        """키움 로그인"""
        try:
            ret = self.kiwoom.CommConnect()
            if ret != 0:
                self._error_exit("로그인 요청 실패")

            # 로그인 대기
            start_time = time.time()
            while not self.connected:
                if time.time() - start_time > timeout:
                    self._error_exit("로그인 타임아웃")
                QApplication.processEvents()
                time.sleep(0.1)

            # 계좌 목록 조회
            self.account_list = self.kiwoom.GetLoginInfo("ACCNO").split(';')[:-1]
            return True

        except Exception as e:
            self._error_exit(f"로그인 실패: {str(e)}")

    def get_accounts(self):
        """계좌 목록 조회"""
        accounts = []
        for account_number in self.account_list:
            accounts.append({
                'account_number': account_number,
                'account_name': f'키움증권 계좌 ({account_number})',
                'account_type': '일반',
                'broker_name': '키움증권'
            })
        return {'success': True, 'data': accounts}

    def get_balance(self, account_number):
        """계좌 잔고 조회"""
        try:
            result = self._request_tr(
                tr_code=self.tr_balance,
                request_name=f"예수금_{account_number}",
                input_data={
                    "계좌번호": account_number,
                    "비밀번호": self.account_password,
                    "비밀번호입력매체구분": self.password_media,
                    "조회구분": "1"
                }
            )

            balance_data = result.get('data', {})

            balance_info = {
                'account_number': account_number,
                'cash_balance': self._parse_float(balance_data.get('cash_balance', '0')),
                'stock_balance': self._parse_float(balance_data.get('stock_balance', '0')),
                'total_balance': self._parse_float(balance_data.get('total_balance', '0')),
                'evaluation_amount': self._parse_float(balance_data.get('stock_balance', '0')),
                'profit_loss': self._parse_float(balance_data.get('profit_loss', '0')),
                'profit_loss_rate': self._parse_float(balance_data.get('profit_loss_rate', '0'))
            }

            return {'success': True, 'data': balance_info}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_holdings(self, account_number):
        """보유종목 조회"""
        try:
            result = self._request_tr(
                tr_code=self.tr_holdings,
                request_name=f"계좌평가_{account_number}",
                input_data={
                    "계좌번호": account_number,
                    "비밀번호": self.account_password,
                    "상장폐지조회구분": self.delisted_filter,
                    "비밀번호입력매체구분": self.password_media,
                    "거래소구분": self.exchange_code
                }
            )

            holdings_data = result.get('data', {})
            holdings = holdings_data.get('holdings', [])

            return {'success': True, 'data': holdings}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _request_tr(self, tr_code, request_name, input_data, timeout=10):
        """TR 요청"""
        try:
            # Queue 생성
            result_queue = Queue()
            self.request_queue[request_name] = result_queue

            # 입력값 설정
            for key, value in input_data.items():
                self.kiwoom.SetInputValue(key, value)

            # TR 요청
            ret = self.kiwoom.CommRqData(request_name, tr_code, 0, "0101")
            if ret != 0:
                raise Exception(f"TR 요청 실패: {ret}")

            # Rate limiting
            time.sleep(0.2)

            # 결과 대기
            start_time = time.time()
            while True:
                QApplication.processEvents()
                try:
                    result = result_queue.get_nowait()
                    return result
                except Empty:
                    if time.time() - start_time > timeout:
                        raise Exception(f"TR 타임아웃: {request_name}")
                    time.sleep(0.1)

        except Exception as e:
            raise Exception(f"TR 요청 실패: {str(e)}")
        finally:
            if request_name in self.request_queue:
                del self.request_queue[request_name]

    def _on_event_connect(self, err_code):
        """로그인 이벤트"""
        self.connected = (err_code == 0)

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, prev_next, *args):
        """TR 데이터 수신"""
        try:
            if rqname not in self.request_queue:
                return

            # 데이터 파싱
            result = self._parse_tr_data(trcode, rqname)

            # Queue에 결과 전달
            self.request_queue[rqname].put(result)

        except Exception as e:
            if rqname in self.request_queue:
                self.request_queue[rqname].put({'error': str(e)})

    def _parse_tr_data(self, trcode, rqname):
        """TR 데이터 파싱"""
        result = {'trcode': trcode, 'rqname': rqname, 'data': {}}

        trcode_upper = trcode.upper()

        if trcode_upper == "OPW00018":  # 예수금
            result['data'] = self._parse_balance_data()
        elif trcode_upper == "OPW00004":  # 계좌평가
            result['data'] = self._parse_holdings_data()

        return result

    def _parse_balance_data(self):
        """예수금 데이터 파싱"""
        return {
            'cash_balance': self._get_comm_data("예수금상세현황요청", 0, "예수금"),
            'stock_balance': self._get_comm_data("예수금상세현황요청", 0, "총평가금액"),
            'total_balance': self._get_comm_data("예수금상세현황요청", 0, "총자산"),
            'profit_loss': self._get_comm_data("예수금상세현황요청", 0, "총손익금액"),
            'profit_loss_rate': self._get_comm_data("예수금상세현황요청", 0, "총수익률(%)")
        }

    def _parse_holdings_data(self):
        """보유종목 데이터 파싱"""
        holdings = []
        count = self.kiwoom.GetRepeatCnt("OPW00004", "계좌평가현황")

        for i in range(count):
            profit_rate_str = self._get_comm_data("OPW00004", i, "손익율")
            try:
                profit_rate = float(profit_rate_str) / 10000 if profit_rate_str else 0.0
            except:
                profit_rate = 0.0

            holding = {
                'symbol': self._get_comm_data("OPW00004", i, "종목코드").strip(),
                'name': self._get_comm_data("OPW00004", i, "종목명").strip(),
                'quantity': self._parse_int(self._get_comm_data("OPW00004", i, "보유수량")),
                'average_price': self._parse_float(self._get_comm_data("OPW00004", i, "매입가")),
                'current_price': self._parse_float(self._get_comm_data("OPW00004", i, "현재가")),
                'evaluation_amount': self._parse_float(self._get_comm_data("OPW00004", i, "평가금액")),
                'profit_loss': self._parse_float(self._get_comm_data("OPW00004", i, "평가손익")),
                'profit_loss_rate': profit_rate
            }

            if holding['symbol']:
                holdings.append(holding)

        return {'holdings': holdings}

    def _get_comm_data(self, trcode, index, item_name):
        """데이터 조회"""
        try:
            data = self.kiwoom.GetCommData(trcode, item_name, index)
            return data.strip() if data else ""
        except:
            return ""

    def _parse_int(self, value):
        """정수 파싱"""
        try:
            return int(value.strip()) if value else 0
        except:
            return 0

    def _parse_float(self, value):
        """실수 파싱"""
        try:
            return float(value.strip().replace(',', '')) if value else 0.0
        except:
            return 0.0

    def _error_exit(self, message):
        """에러 메시지 출력 후 종료"""
        print(json.dumps({'success': False, 'error': message}, ensure_ascii=False))
        sys.exit(1)

    def disconnect(self):
        """연결 해제"""
        try:
            if self.kiwoom and self.connected:
                self.kiwoom.CommTerminate()
        except:
            pass


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': '명령어가 필요합니다'}, ensure_ascii=False))
        sys.exit(1)

    command = sys.argv[1]

    # Qt 애플리케이션 생성
    app = QApplication(sys.argv)

    # Worker 생성 및 초기화
    worker = KiwoomWorker()
    worker.initialize()
    worker.login()

    # 명령 실행
    try:
        if command == 'get_accounts':
            result = worker.get_accounts()
        elif command == 'get_balance':
            if len(sys.argv) < 3:
                result = {'success': False, 'error': '계좌번호가 필요합니다'}
            else:
                account_number = sys.argv[2]
                result = worker.get_balance(account_number)
        elif command == 'get_holdings':
            if len(sys.argv) < 3:
                result = {'success': False, 'error': '계좌번호가 필요합니다'}
            else:
                account_number = sys.argv[2]
                result = worker.get_holdings(account_number)
        else:
            result = {'success': False, 'error': f'알 수 없는 명령어: {command}'}

        # 결과 출력 (JSON)
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False))
    finally:
        worker.disconnect()

    sys.exit(0)


if __name__ == '__main__':
    main()
