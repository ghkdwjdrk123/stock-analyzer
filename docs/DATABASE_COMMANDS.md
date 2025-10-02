# Stock Analyzer Database Commands

DB 테이블들을 표 형태로 출력할 수 있는 명령어들

## 📋 개요

Stock Analyzer 프로젝트의 데이터베이스를 쉽게 조회하고 분석할 수 있는 5가지 도구를 제공합니다:

1. **view_database.py** - 상세한 테이블 조회 및 필터링
2. **db_commands.py** - 빠른 조회 명령어
3. **db_analysis.py** - 고급 분석 도구
4. **show_table_columns.py** - 데이터베이스 스키마 조회
5. **db.bat** - Windows 배치 스크립트 (간편 사용)

**주요 특징**: 10개 테이블, 149개 컬럼의 완전한 포트폴리오 분석 시스템

## 🚀 설치 요구사항

```bash
pip install tabulate
```

## 📊 1. view_database.py - 상세 테이블 조회

### 기본 사용법

```bash
# 전체 테이블 요약
python view_database.py --summary

# 테이블 관계 조회
python view_database.py --relations

# 특정 테이블 조회
python view_database.py [테이블명] [옵션]
```

### 테이블별 조회 명령어

```bash
# 브로커 정보
python view_database.py brokers

# 계좌 정보
python view_database.py accounts

# 잔고 정보 (최근 50개)
python view_database.py balances

# 보유종목 (현재 보유 중인 것만)
python view_database.py holdings

# 거래내역 (최근 50개)
python view_database.py transactions

# 월별 요약
python view_database.py monthly

# 종목별 성과
python view_database.py performances
```

### 조회 옵션

```bash
# 조회 개수 제한
python view_database.py holdings --limit 20

# 특정 계좌만 조회
python view_database.py balances --account-id 1

# 모든 레코드 조회 (limit 무시)
python view_database.py transactions --all
```

### 실제 사용 예시

```bash
# 최근 10개 거래내역
python view_database.py transactions -l 10

# 계좌 ID 1의 보유종목
python view_database.py holdings --account-id 1 --limit 5

# 모든 잔고 데이터
python view_database.py balances --all
```

## ⚡ 2. db_commands.py - 빠른 조회

### 사용 가능한 명령어

```bash
# DB 상태 및 전체 요약
python db_commands.py status

# 최신 데이터 현황
python db_commands.py latest

# 상위 보유종목 (기본 10개)
python db_commands.py holdings

# 최근 거래내역 (기본 10개)
python db_commands.py transactions

# 계좌별 수익률 요약
python db_commands.py performance
```

## 📈 3. db_analysis.py - 고급 분석

### 분석 유형

```bash
# 포트폴리오 분포 분석
python db_analysis.py portfolio

# 섹터 집중도 분석 (종목명 기반 추정)
python db_analysis.py sector

# 거래 패턴 분석 (최근 30일)
python db_analysis.py trading

# 수익률 추이 분석 (최근 30일)
python db_analysis.py performance

# 상위/하위 수익 종목
python db_analysis.py top

# 위험 지표 분석
python db_analysis.py risk

# 전체 분석 실행
python db_analysis.py all
```

## 🖥️ 4. db.bat - Windows 배치 스크립트

### 간편한 Windows 명령어

```bash
# 도움말
db

# DB 상태
db status

# 계좌 조회
db accounts

# 잔고 조회
db balances

# 보유종목 조회
db holdings

# 거래내역 조회
db transactions

# 브로커 조회
db brokers

# 테이블 관계
db relations
```

### 빠른 조회 명령어

```bash
# 최신 데이터
db latest

# 상위 보유종목
db top

# 최근 거래내역
db recent

# 수익률 요약
db profit
```

### 옵션 사용

```bash
# 20개만 조회
db holdings --limit 20

# 특정 계좌 조회
db balances --account-id 1
```

## 📋 데이터베이스 테이블 구조

### 핵심 테이블

| 테이블명 | 설명 | 주요 컬럼 |
|---------|------|-----------|
| **brokers** | 브로커 정보 | name, api_type, platform, enabled |
| **accounts** | 계좌 정보 | broker_id, account_number, account_type, is_active |
| **daily_balances** | 일일 잔고 | account_id, balance_date, total_balance, profit_loss |
| **holdings** | 보유종목 | account_id, symbol, name, quantity, evaluation_amount |
| **transactions** | 거래내역 | account_id, transaction_date, symbol, transaction_type |

### 분석 테이블

| 테이블명 | 설명 | 용도 |
|---------|------|------|
| **monthly_summaries** | 월별 요약 | 월간 성과 집계 |
| **stock_performances** | 종목별 성과 | 종목별 수익률 분석 |
| **portfolio_analyses** | 포트폴리오 분석 | 포트폴리오 위험/수익 지표 |
| **trading_patterns** | 거래 패턴 | 거래 행동 분석 |
| **risk_metrics** | 위험 지표 | 리스크 관리 지표 |

## 🔗 테이블 관계

```
brokers (1) ──→ (N) accounts
accounts (1) ──→ (N) daily_balances
accounts (1) ──→ (N) holdings
accounts (1) ──→ (N) transactions
accounts (1) ──→ (N) [분석 테이블들]
```

## 💡 사용 팁

### 1. 일상적인 모니터링

```bash
# 매일 체크할 명령어들
db status              # 전체 현황
db latest              # 최신 데이터
db profit              # 수익률 요약
```

### 2. 상세 분석

```bash
# 포트폴리오 분석
python db_analysis.py all

# 특정 기간 거래 분석
python view_database.py transactions --limit 100
```

### 3. 문제 해결

```bash
# 데이터 누락 확인
python view_database.py --summary

# 특정 계좌 문제 확인
python view_database.py balances --account-id [ID]
```

### 4. 성능 최적화

```bash
# 제한된 조회로 빠른 확인
python view_database.py holdings -l 10

# 전체 데이터 필요시
python view_database.py holdings --all
```

## 📊 5. show_table_columns.py - 스키마 조회

### 사용법

```bash
# 모든 테이블 컬럼 정보
python show_table_columns.py all

# 테이블 요약 정보
python show_table_columns.py summary

# 특정 테이블 컬럼 정보
python show_table_columns.py [테이블명]
```

### 주요 기능

- **전체 스키마**: 149개 컬럼의 상세 정보 (데이터 타입, NULL 허용 여부, 기본값)
- **테이블별 조회**: 특정 테이블의 컬럼 구조만 확인
- **요약 정보**: 테이블별 컬럼 수와 주요 컬럼 목록

## ⚠️ 주의사항

1. **인코딩 문제**: Windows 콘솔에서 일부 특수문자가 깨질 수 있습니다
2. **대용량 데이터**: `--all` 옵션 사용 시 조회 시간이 오래 걸릴 수 있습니다
3. **권한**: 데이터베이스 파일에 대한 읽기 권한이 필요합니다
4. **동시 접근**: GUI 실행 중에는 일부 명령어가 제한될 수 있습니다
5. **거래내역**: 현재 거래내역 테이블은 비어있음 (API 미구현)

## 🔧 문제 해결

### 자주 발생하는 오류

1. **Database connection failed**
   - `config/config.json` 확인
   - 데이터베이스 파일 존재 여부 확인

2. **Module not found: tabulate**
   ```bash
   pip install tabulate
   ```

3. **Permission denied**
   - 관리자 권한으로 실행
   - 파일 경로 권한 확인

### 로그 확인

```bash
# 애플리케이션 로그 확인
cat logs/stock_analyzer.log
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. `README.md` - 전체 설정 가이드
2. `CLAUDE.md` - 개발자 가이드
3. `logs/` 디렉토리 - 오류 로그

---

**Stock Analyzer Database Commands v1.0**
*효율적인 포트폴리오 데이터 관리를 위한 도구*