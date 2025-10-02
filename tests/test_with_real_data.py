"""
실제 데이터로 차트 및 분석 기능 테스트
"""
import os
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.utils.config import ConfigManager
from app.utils.database import db_manager, get_database_url
from app.utils.logger import setup_logging, get_logger
from app.utils.chart_generator import ChartGenerator
from app.services.broker_service import BrokerService
from app.services.analysis_service import AnalysisService
from app.models.broker import Broker
from app.models.account import Account
from app.models.balance import DailyBalance
from app.models.holding import Holding
from app.models.transaction import Transaction

def collect_and_store_real_data():
    """실제 데이터 수집 및 저장"""
    try:
        # 설정 로드
        config_manager = ConfigManager()
        config = config_manager.config
        
        # 로깅 설정
        setup_logging(config)
        logger = get_logger(__name__)
        logger.info("실제 데이터 수집 및 차트 테스트를 시작합니다.")
        
        # 데이터베이스 초기화
        database_config = config.get('database', {})
        database_url = get_database_url(database_config)
        db_manager.init_database(database_url)
        logger.info("데이터베이스 초기화 완료")
        
        # 브로커 서비스 초기화
        broker_service = BrokerService(config)
        logger.info("브로커 서비스 초기화 완료")
        
        # 한국투자증권 브로커 연결
        kis_broker = broker_service.get_broker("한국투자증권")
        if not kis_broker:
            logger.error("한국투자증권 브로커를 찾을 수 없습니다.")
            return False
        
        # API 연결
        logger.info("한국투자증권 API 연결을 시도합니다.")
        if not kis_broker.connect():
            logger.error("한국투자증권 API 연결에 실패했습니다.")
            return False
        
        logger.info("한국투자증권 API 연결 성공!")
        
        # 세션 가져오기
        session = db_manager.get_session()
        
        try:
            # 1. 브로커 데이터 저장
            logger.info("1. 브로커 데이터 저장")
            existing_broker = session.query(Broker).filter_by(name="한국투자증권").first()
            if not existing_broker:
                broker = Broker(
                    name="한국투자증권",
                    api_type="kis",
                    platform="cross",
                    enabled=True,
                    description="한국투자증권 Open API"
                )
                session.add(broker)
                session.commit()
                logger.info("브로커 데이터 저장 완료")
            else:
                broker = existing_broker
                logger.info("기존 브로커 데이터 사용")
            
            # 2. 계좌 데이터 저장
            logger.info("2. 계좌 데이터 저장")
            accounts = kis_broker.get_accounts()
            if not accounts:
                logger.error("계좌 정보를 가져올 수 없습니다.")
                return False
            
            account_data = accounts[0]
            existing_account = session.query(Account).filter_by(
                account_number=account_data['account_number']
            ).first()
            
            if not existing_account:
                account = Account(
                    broker_id=broker.id,
                    account_number=account_data['account_number'],
                    account_name=account_data['account_name'],
                    account_type=account_data['account_type'],
                    is_active=True
                )
                session.add(account)
                session.commit()
                logger.info("계좌 데이터 저장 완료")
            else:
                account = existing_account
                logger.info("기존 계좌 데이터 사용")
            
            # 3. 현재 잔고 데이터 저장
            logger.info("3. 현재 잔고 데이터 저장")
            balance_data = kis_broker.get_balance(account_data['account_number'])
            
            # 오늘 날짜의 잔고 데이터가 있는지 확인
            today = date.today()
            existing_balance = session.query(DailyBalance).filter_by(
                account_id=account.id,
                balance_date=today
            ).first()
            
            if not existing_balance:
                daily_balance = DailyBalance(
                    account_id=account.id,
                    balance_date=today,
                    cash_balance=balance_data.get('cash_balance', 0),
                    stock_balance=balance_data.get('stock_balance', 0),
                    total_balance=balance_data.get('total_balance', 0),
                    evaluation_amount=balance_data.get('evaluation_amount', 0),
                    profit_loss=balance_data.get('profit_loss', 0),
                    profit_loss_rate=balance_data.get('profit_loss_rate', 0)
                )
                session.add(daily_balance)
                session.commit()
                logger.info("일일 잔고 데이터 저장 완료")
            else:
                daily_balance = existing_balance
                logger.info("기존 일일 잔고 데이터 사용")
            
            # 4. 보유종목 데이터 저장
            logger.info("4. 보유종목 데이터 저장")
            holdings_data = kis_broker.get_holdings(account_data['account_number'])
            
            for holding_data in holdings_data:
                existing_holding = session.query(Holding).filter_by(
                    account_id=account.id,
                    symbol=holding_data['symbol']
                ).first()
                
                if existing_holding:
                    # 기존 데이터 업데이트
                    existing_holding.quantity = holding_data.get('quantity', 0)
                    existing_holding.average_price = holding_data.get('average_price', 0)
                    existing_holding.current_price = holding_data.get('current_price', 0)
                    existing_holding.evaluation_amount = holding_data.get('evaluation_amount', 0)
                    existing_holding.profit_loss = holding_data.get('profit_loss', 0)
                    existing_holding.profit_loss_rate = holding_data.get('profit_loss_rate', 0)
                    existing_holding.last_updated = datetime.utcnow()
                else:
                    # 새 데이터 생성
                    holding = Holding(
                        account_id=account.id,
                        symbol=holding_data['symbol'],
                        name=holding_data['name'],
                        quantity=holding_data.get('quantity', 0),
                        average_price=holding_data.get('average_price', 0),
                        current_price=holding_data.get('current_price', 0),
                        evaluation_amount=holding_data.get('evaluation_amount', 0),
                        profit_loss=holding_data.get('profit_loss', 0),
                        profit_loss_rate=holding_data.get('profit_loss_rate', 0)
                    )
                    session.add(holding)
            
            session.commit()
            logger.info("보유종목 데이터 저장 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"데이터 저장 중 오류 발생: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()
            kis_broker.disconnect()
            
    except Exception as e:
        logger.error(f"실제 데이터 수집 실패: {str(e)}")
        return False

def test_charts_with_real_data():
    """실제 데이터로 차트 테스트"""
    try:
        logger = get_logger(__name__)
        logger.info("실제 데이터로 차트 테스트를 시작합니다.")
        
        # 차트 생성기 초기화
        chart_generator = ChartGenerator()
        logger.info("차트 생성기 초기화 완료")
        
        # 세션 가져오기
        session = db_manager.get_session()
        
        try:
            # 1. 계좌 정보 가져오기
            account = session.query(Account).filter_by(is_active=True).first()
            if not account:
                logger.error("활성 계좌를 찾을 수 없습니다.")
                return False
            
            logger.info(f"테스트 계좌: {account.account_name} ({account.account_number})")
            
            # 2. 일일 잔고 데이터 가져오기 (최근 30일)
            thirty_days_ago = date.today() - timedelta(days=30)
            daily_balances = session.query(DailyBalance).filter(
                DailyBalance.account_id == account.id,
                DailyBalance.balance_date >= thirty_days_ago
            ).order_by(DailyBalance.balance_date).all()
            
            # 차트용 데이터 변환
            balance_chart_data = []
            for balance in daily_balances:
                balance_chart_data.append({
                    'balance_date': balance.balance_date,
                    'cash_balance': balance.cash_balance,
                    'stock_balance': balance.stock_balance,
                    'total_balance': balance.total_balance,
                    'evaluation_amount': balance.evaluation_amount,
                    'profit_loss': balance.profit_loss,
                    'profit_loss_rate': balance.profit_loss_rate
                })
            
            # 3. 보유종목 데이터 가져오기
            holdings = session.query(Holding).filter_by(account_id=account.id).all()
            
            # 차트용 데이터 변환
            holdings_chart_data = []
            for holding in holdings:
                holdings_chart_data.append({
                    'symbol': holding.symbol,
                    'name': holding.name,
                    'quantity': holding.quantity,
                    'average_price': holding.average_price,
                    'current_price': holding.current_price,
                    'evaluation_amount': holding.evaluation_amount,
                    'profit_loss': holding.profit_loss,
                    'profit_loss_rate': holding.profit_loss_rate
                })
            
            # 4. 차트 생성
            logger.info("4.1 포트폴리오 성과 차트 생성")
            if balance_chart_data:
                portfolio_chart = chart_generator.create_portfolio_performance_chart(balance_chart_data)
                logger.info("포트폴리오 성과 차트 생성 완료")
            else:
                logger.warning("잔고 데이터가 없어 포트폴리오 차트를 생성할 수 없습니다.")
                portfolio_chart = None
            
            logger.info("4.2 보유종목 비중 파이 차트 생성")
            if holdings_chart_data:
                holdings_pie_chart = chart_generator.create_holdings_pie_chart(holdings_chart_data)
                logger.info("보유종목 비중 파이 차트 생성 완료")
                
                holdings_perf_chart = chart_generator.create_holdings_performance_chart(holdings_chart_data)
                logger.info("보유종목 성과 차트 생성 완료")
            else:
                logger.warning("보유종목 데이터가 없어 보유종목 차트를 생성할 수 없습니다.")
                holdings_pie_chart = None
                holdings_perf_chart = None
            
            # 5. 차트 HTML 내보내기
            logger.info("5. 차트 HTML 내보내기")
            os.makedirs("./data/charts", exist_ok=True)
            
            if portfolio_chart:
                try:
                    portfolio_html = chart_generator.export_chart_to_html(portfolio_chart, "real_portfolio_performance.html")
                    logger.info(f"포트폴리오 차트 HTML 저장: {portfolio_html}")
                except Exception as e:
                    logger.warning(f"포트폴리오 차트 HTML 저장 실패: {str(e)}")
            
            if holdings_pie_chart:
                try:
                    holdings_html = chart_generator.export_chart_to_html(holdings_pie_chart, "real_holdings_pie.html")
                    logger.info(f"보유종목 파이 차트 HTML 저장: {holdings_html}")
                except Exception as e:
                    logger.warning(f"보유종목 파이 차트 HTML 저장 실패: {str(e)}")
            
            if holdings_perf_chart:
                try:
                    perf_html = chart_generator.export_chart_to_html(holdings_perf_chart, "real_holdings_performance.html")
                    logger.info(f"보유종목 성과 차트 HTML 저장: {perf_html}")
                except Exception as e:
                    logger.warning(f"보유종목 성과 차트 HTML 저장 실패: {str(e)}")
            
            # 6. 분석 서비스 테스트
            logger.info("6. 분석 서비스 테스트")
            analysis_service = AnalysisService()
            
            try:
                # 월별 요약 생성
                current_date = date.today()
                monthly_summary = analysis_service.generate_monthly_summary(
                    account.id, current_date.year, current_date.month
                )
                if monthly_summary:
                    logger.info(f"월별 요약 생성 성공: 총자산 {monthly_summary.total_balance:,.0f}원")
                
                # 포트폴리오 분석 생성
                portfolio_analysis = analysis_service.generate_portfolio_analysis(account.id)
                if portfolio_analysis:
                    logger.info(f"포트폴리오 분석 생성 성공: 총자산 {portfolio_analysis.total_assets:,.0f}원")
                
            except Exception as e:
                logger.warning(f"분석 서비스 테스트 실패: {str(e)}")
            finally:
                analysis_service.close_session()
            
            logger.info("실제 데이터로 차트 테스트가 완료되었습니다!")
            return True
            
        except Exception as e:
            logger.error(f"차트 테스트 실패: {str(e)}")
            return False
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"실제 데이터 차트 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 실제 데이터로 차트 및 분석 테스트 ===")
    
    # 1. 실제 데이터 수집 및 저장
    print("\n1. 실제 데이터 수집 및 저장")
    data_success = collect_and_store_real_data()
    
    if data_success:
        # 2. 실제 데이터로 차트 테스트
        print("\n2. 실제 데이터로 차트 테스트")
        chart_success = test_charts_with_real_data()
        
        # 결과 출력
        print("\n=== 테스트 결과 ===")
        print(f"실제 데이터 수집: {'Success' if data_success else 'Failed'}")
        print(f"차트 생성 테스트: {'Success' if chart_success else 'Failed'}")
        
        if chart_success:
            print("\nSuccess: 실제 데이터로 차트 및 분석 테스트가 성공적으로 완료되었습니다!")
            print("Charts: 생성된 차트 파일들을 ./data/charts/ 디렉토리에서 확인할 수 있습니다.")
            print("   - real_portfolio_performance.html (포트폴리오 성과)")
            print("   - real_holdings_pie.html (보유종목 비중)")
            print("   - real_holdings_performance.html (보유종목 성과)")
        else:
            print("\nWarning: 차트 생성 테스트가 실패했습니다.")
    else:
        print("\nError: 실제 데이터 수집에 실패했습니다.")
    
    print("\n테스트 완료!")
