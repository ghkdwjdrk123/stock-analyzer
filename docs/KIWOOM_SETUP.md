# 키움증권 API 설정 가이드

## 개요

키움증권 OpenAPI+는 32비트 COM/OCX 기반이므로, 본 프로젝트는 **32비트 서브프로세스 방식**으로 구현되어 있습니다.

- **메인 프로그램**: 64비트 Python 환경
- **키움 API 전용**: 32비트 Python 서브프로세스

## 1. 32비트 Python 설치

### Windows 환경

1. **32비트 Python 다운로드**
   - https://www.python.org/downloads/windows/
   - Python 3.9 또는 3.10 권장
   - **중요**: "Windows installer (32-bit)" 다운로드

2. **설치 옵션**
   ```
   설치 경로 예시: C:\Python39-32

   체크할 옵션:
   ☑ Add Python 3.9 to PATH (선택 사항)
   ☑ Install for all users (권장)
   ```

3. **설치 확인**
   ```bash
   # 명령 프롬프트에서
   C:\Python39-32\python.exe --version
   # 출력: Python 3.9.x

   # 32비트 확인
   C:\Python39-32\python.exe -c "import struct; print(struct.calcsize('P') * 8)"
   # 출력: 32
   ```

## 2. 키움 OpenAPI+ 모듈 설치

### 공식 모듈 다운로드 및 설치

1. **키움증권 홈페이지 접속**
   - https://www.kiwoom.com
   - 고객서비스 → 다운로드 → Open API

2. **키움 Open API+ 모듈 다운로드**
   - "키움 Open API+ 모듈" 설치 파일 다운로드
   - **관리자 권한**으로 설치 실행

3. **기본 설치 경로**
   ```
   C:\OpenAPI\
   ```

### OCX 등록 (32비트)

관리자 권한 명령 프롬프트에서 실행:

```bash
# 32비트 레지스트리에 등록
C:\Windows\SysWOW64\regsvr32.exe C:\OpenAPI\khopenapi.ocx

# 성공 메시지 확인
# "C:\OpenAPI\khopenapi.ocx의 DllRegisterServer 성공했습니다."
```

### 버전 처리 실행

```bash
# OpenAPI 버전 업데이트
C:\OpenAPI\opversionup.exe
```

## 3. 32비트 Python 패키지 설치

32비트 Python 환경에서 필요한 패키지 설치:

```bash
# 32비트 Python으로 패키지 설치
C:\Python39-32\python.exe -m pip install pywin32==306
C:\Python39-32\python.exe -m pip install PyQt5==5.15.10
C:\Python39-32\python.exe -m pip install python-dotenv
```

## 4. 환경변수 설정

### env 파일 설정

프로젝트 루트의 `env` 파일에 다음 추가:

```bash
# 32비트 Python 경로
PYTHON32_PATH=C:\Python39-32\python.exe

# 키움증권 계좌 정보
KIWOOM_ACCOUNT_NUMBER=your_10_digit_account_number
KIWOOM_ACCOUNT_PASSWORD=your_account_password
KIWOOM_CERT_PASSWORD=your_certificate_password

# 조회 설정
KIWOOM_DELISTED_FILTER=0
KIWOOM_PASSWORD_MEDIA=00
KIWOOM_EXCHANGE_CODE=KRX

# TR 코드
KIWOOM_TR_BALANCE=opw00018
KIWOOM_TR_HOLDINGS=OPW00004
KIWOOM_TR_ACCOUNT_EVAL=opw00001
```

**중요**: `PYTHON32_PATH`를 실제 32비트 Python 설치 경로로 설정하세요.

## 5. 설치 확인

### 레지스트리 확인

```bash
# ProgID 확인
reg query "HKEY_CLASSES_ROOT\KHOPENAPI.KHOpenAPICtrl.1"

# CLSID 확인 (32비트)
reg query "HKEY_CLASSES_ROOT\WOW6432Node\CLSID\{A1574A0D-6BFA-4BD7-9020-DED88711818D}\InprocServer32"
```

### Worker 스크립트 테스트

```bash
# 프로젝트 루트에서
C:\Python39-32\python.exe kiwoom_worker_32.py get_accounts
```

**예상 출력** (로그인 창이 뜨면 로그인):
```json
{
  "success": true,
  "data": [
    {
      "account_number": "1234567890",
      "account_name": "키움증권 계좌 (1234567890)",
      "account_type": "일반",
      "broker_name": "키움증권"
    }
  ]
}
```

## 6. 문제 해결

### OCX 등록 실패

```bash
# 64비트가 아닌 32비트 regsvr32 사용 확인
# ❌ 틀린 방법:
C:\Windows\System32\regsvr32.exe C:\OpenAPI\khopenapi.ocx

# ✅ 올바른 방법:
C:\Windows\SysWOW64\regsvr32.exe C:\OpenAPI\khopenapi.ocx
```

### Python 32비트 확인

```python
import struct
print(f"Python 비트: {struct.calcsize('P') * 8}비트")
# 출력: Python 비트: 32비트
```

### Worker 실행 오류

```bash
# 오류: python을 찾을 수 없습니다
# → env 파일의 PYTHON32_PATH 확인

# 오류: No module named 'PyQt5'
# → 32비트 Python에 PyQt5 설치 확인
C:\Python39-32\python.exe -m pip list | findstr PyQt5
```

### OCX 로드 실패

```python
# 오류: 'QAxWidget' object has no attribute 'OnEventConnect'
# 원인: OCX가 제대로 등록되지 않음
# 해결:
# 1. 관리자 권한으로 regsvr32 재실행
# 2. opversionup.exe 실행
# 3. 키움 OpenAPI+ 모듈 재설치
```

### VC++ 런타임 오류

```bash
# mfc100.dll 또는 msvcr100.dll 오류 발생 시
# Microsoft Visual C++ 재배포 가능 패키지 설치
# https://www.microsoft.com/ko-kr/download/details.aspx?id=26999
```

## 7. 사용 방법

### 일반 사용자

프로젝트를 실행하면 **자동으로 32비트 서브프로세스가 실행**됩니다.

```bash
# GUI 실행
python run_gui.py

# 메인 프로그램 실행
python main.py
```

"데이터 수집" 버튼 클릭 시:
- KIS 계좌: 64비트 메인 프로세스에서 REST API 호출
- 키움 계좌: 자동으로 32비트 서브프로세스 실행 → 데이터 수집 → 결과 반환

### 개발자

```python
from app.brokers.kiwoom_broker import KiwoomBroker

# 브로커 생성 (64비트 환경)
broker = KiwoomBroker(config)

# 메서드 호출 → 내부적으로 32비트 서브프로세스 실행
accounts = broker.get_accounts()
balance = broker.get_balance(account_number)
holdings = broker.get_holdings(account_number)
```

## 8. 아키텍처

```
┌─────────────────────────────────────────────┐
│ 메인 프로그램 (64비트 Python)               │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │ KIS Broker   │      │ Kiwoom Broker   │ │
│  │ (REST API)   │      │ (Subprocess)    │ │
│  └──────────────┘      └────────┬────────┘ │
│         │                       │          │
└─────────┼───────────────────────┼──────────┘
          │                       │
          │                       │ subprocess.run()
          │                       ▼
          │              ┌─────────────────────┐
          │              │ kiwoom_worker_32.py │
          │              │ (32비트 Python)     │
          │              │                     │
          │              │  ┌──────────────┐   │
          │              │  │ QAxWidget    │   │
          │              │  │ (OCX 로드)   │   │
          │              │  └──────────────┘   │
          │              └─────────────────────┘
          │                       │
          ▼                       ▼
    [한투 서버]            [키움 서버]
```

## 참고 자료

- [키움증권 OpenAPI+ 공식 가이드](https://www.kiwoom.com/h/customer/download/VOpenApiInfoView)
- [키움 OpenAPI+ 파이썬 개발가이드 (WikiDocs)](https://wikidocs.net/book/1173)
- [Python 32비트 다운로드](https://www.python.org/downloads/windows/)
- [Microsoft VC++ 재배포 가능 패키지](https://support.microsoft.com/ko-kr/help/2977003)
