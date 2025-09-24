# Stock Analyzer

한국투자증권 API를 활용한 계좌 자동 분석 프로그램입니다.

## 주요 기능

- 한국투자증권 API 연동
- 계좌 정보 자동 조회
- 잔고 및 보유종목 조회
- 거래내역 수집
- **토큰 파일 관리** (자동 저장/로드/갱신)
- 데이터베이스 저장 및 관리
- 로깅 및 에러 처리

## 프로젝트 구조

```
Stock Analyzer/
├── app/
│   ├── brokers/          # 브로커 API 연동
│   ├── models/           # 데이터베이스 모델
│   ├── services/         # 비즈니스 로직
│   ├── utils/            # 유틸리티
│   └── main.py           # 메인 애플리케이션
├── config/               # 설정 파일
├── data/                 # 데이터베이스 파일
├── token/                # 토큰 파일 (증권사별)
│   ├── kis/              # 한국투자증권 토큰
│   └── kiwoom/           # 키움증권 토큰
├── logs/                 # 로그 파일
├── rules/                # 참고 자료
├── main.py               # 실행 파일
├── test_token_manager.py # 토큰 관리 테스트
└── manage_tokens.py      # 토큰 관리 유틸리티
```

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`env.example` 파일을 참고하여 `env` 파일을 생성하고 민감한 정보를 설정하세요:

```bash
# env 파일 생성
cp env.example env

# env 파일 편집하여 실제 값 입력
# 한국투자증권 API 키 설정
KIS_APP_KEY=your_actual_app_key
KIS_APP_SECRET=your_actual_app_secret

# 이메일 알림 설정 (선택사항)
EMAIL_USERNAME=your_actual_email@gmail.com
EMAIL_PASSWORD=your_actual_email_password
```

### 3. 설정 파일 확인

`config/config.json` 파일은 일반적인 설정을 포함하며, 민감한 정보는 환경변수에서 로드됩니다.

## 사용법

### 1. 기본 실행

```bash
python main.py
```

### 2. 토큰 관리

```bash
# 토큰 관리 테스트
python test_token_manager.py

# 토큰 상태 조회
python manage_tokens.py status

# 모든 토큰 삭제
python manage_tokens.py clear

# 특정 브로커 토큰 삭제
python manage_tokens.py delete "kis"
python manage_tokens.py delete "kiwoom"
```

### 3. 한국투자증권 API 키 발급

1. [한국투자증권 OpenAPI](https://apiportal.koreainvestment.com/) 접속
2. 회원가입 및 로그인
3. 앱 등록 후 App Key, App Secret 발급
4. 설정 파일에 키 정보 입력

## 주요 클래스

### KISBroker
한국투자증권 API 연동을 담당하는 클래스입니다.

```python
from app.brokers.kis_broker import KISBroker

# 브로커 초기화
broker = KISBroker(config)

# API 연결
broker.connect()

# 계좌 목록 조회
accounts = broker.get_accounts()

# 잔고 조회
balance = broker.get_balance(account_number)

# 보유종목 조회
holdings = broker.get_holdings(account_number)
```

### BrokerService
여러 브로커를 관리하는 서비스 클래스입니다.

```python
from app.services.broker_service import BrokerService

# 서비스 초기화
broker_service = BrokerService(config)

# 모든 계좌 조회
accounts = broker_service.get_all_accounts()

# 특정 계좌 잔고 조회
balance = broker_service.get_account_balance("한국투자증권", account_number)
```

### DataCollector
데이터 수집 및 저장을 담당하는 클래스입니다.

```python
from app.services.data_collector import DataCollector

# 데이터 수집기 초기화
collector = DataCollector(broker_service)

# 전체 계좌 데이터 수집
collector.collect_all_accounts()

# 특정 계좌 데이터 수집
collector.collect_account_data("한국투자증권", account_number)
```

### TokenManager
증권사별 토큰 파일 관리를 담당하는 클래스입니다.

> 📖 **자세한 내용**: `rules/common.mdc` 파일을 참조하세요.

```python
from app.utils.token_manager import TokenManager

# 증권사별 토큰 관리자 초기화
kis_token_manager = TokenManager(broker_name="kis")
kiwoom_token_manager = TokenManager(broker_name="kiwoom")

# 토큰 저장
kis_token_manager.save_token(access_token, refresh_token, expires_in)

# 토큰 조회
access_token = kis_token_manager.get_access_token()

# 토큰 유효성 확인
is_valid = kis_token_manager.is_token_valid()

# 토큰 상태 정보
token_info = kis_token_manager.get_token_expiry_info()
```

## 데이터베이스 모델

### Account (계좌)
- 계좌번호, 계좌명, 계좌타입 등 기본 정보

### DailyBalance (일일잔고)
- 일별 현금잔고, 주식잔고, 총잔고 등

### Holding (보유종목)
- 종목코드, 종목명, 수량, 평균단가, 현재가 등

### Transaction (거래내역)
- 거래일자, 종목, 거래구분, 수량, 단가, 거래금액 등

## 로깅

애플리케이션은 다음과 같은 로그를 생성합니다:

- `logs/stock_analyzer.log`: 메인 로그 파일
- 로그 레벨: INFO, DEBUG, WARNING, ERROR
- 민감정보 자동 마스킹

## 보안 및 Git 관리

### 1. 민감정보 보호
- **환경변수 사용**: API 키, 비밀번호 등은 `env` 파일에 저장
- **Git 제외**: `.gitignore`에 의해 민감한 파일들이 Git에 올라가지 않음
- **토큰 관리**: `token/` 폴더에 토큰 파일 저장 (Git 제외)

### 2. Git 사용 시 주의사항
```bash
# Git에 올라가지 않는 파일들
env                    # 환경변수 (민감정보)
config/config.json     # 설정 파일 (민감정보 포함 가능)
token/                 # 토큰 파일들 (증권사별)
├── kis/              # 한국투자증권 토큰
└── kiwoom/           # 키움증권 토큰
data/                  # 데이터베이스 파일들
logs/                  # 로그 파일들
```

### 3. 프로젝트 공유 시
- `env.example` 파일을 참고하여 `env` 파일 생성
- 실제 API 키는 개별적으로 설정
- `config/config.json`은 템플릿으로 사용

## 주의사항

1. **API 키 보안**: API 키는 환경변수로 관리하고 설정 파일에 직접 입력하지 마세요.
2. **Rate Limiting**: 한국투자증권 API는 초당 10회, 분당 100회 호출 제한이 있습니다.
3. **토큰 갱신**: 액세스 토큰은 24시간 후 만료되므로 자동 갱신이 필요합니다.
4. **에러 처리**: API 호출 실패 시 재시도 로직이 구현되어 있습니다.

## 문제 해결

### 1. API 연결 실패
- API 키와 시크릿이 올바른지 확인
- 네트워크 연결 상태 확인
- 한국투자증권 API 서버 상태 확인

### 2. 토큰 만료
- 앱이 자동으로 토큰을 갱신합니다
- 수동 갱신이 필요한 경우 브로커 재연결

### 3. 데이터베이스 오류
- 데이터베이스 파일 권한 확인
- SQLite 파일 경로 확인

## 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.
