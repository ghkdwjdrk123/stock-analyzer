#!/usr/bin/env python3
"""
Stock Analyzer Database Analysis Tools
DB 분석 및 통계 조회 도구

고급 분석 기능 제공
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from tabulate import tabulate
from sqlalchemy import func, desc, and_, or_
from typing import List, Dict, Any, Optional

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from view_database import DatabaseViewer
from app.models.broker import Broker
from app.models.account import Account
from app.models.balance import DailyBalance
from app.models.holding import Holding
from app.models.transaction import Transaction

class DatabaseAnalyzer(DatabaseViewer):
    """데이터베이스 분석 클래스"""

    def analyze_portfolio_distribution(self):
        """포트폴리오 분포 분석"""
        # 계좌별 자산 분포
        asset_distribution = self.session.query(
            Account.id,
            Broker.name.label('broker_name'),
            Account.account_number,
            func.sum(Holding.evaluation_amount).label('total_stocks'),
            func.count(Holding.id).label('stock_count')
        ).join(Broker).join(Holding)\
         .filter(Holding.quantity > 0)\
         .group_by(Account.id, Broker.name, Account.account_number)\
         .all()

        print("=" * 100)
        print("📊 포트폴리오 분포 분석")
        print("=" * 100)

        if not asset_distribution:
            print("❌ 포트폴리오 데이터가 없습니다.")
            return

        data = []
        total_value = 0
        total_stocks = 0

        for dist in asset_distribution:
            total_value += dist.total_stocks or 0
            total_stocks += dist.stock_count or 0

            data.append([
                f"{dist.broker_name}-{dist.account_number}",
                f"{dist.total_stocks:,.0f}" if dist.total_stocks else "0",
                f"{dist.stock_count}",
                f"{(dist.total_stocks/sum(d.total_stocks or 0 for d in asset_distribution)*100):.1f}%" if dist.total_stocks else "0.0%"
            ])

        print(tabulate(data,
                      headers=["계좌", "주식가치", "종목수", "비중"],
                      tablefmt="grid"))

        print(f"\n📈 전체 요약:")
        print(f"   총 주식가치: {total_value:,.0f}원")
        print(f"   총 종목수: {total_stocks}개")
        print(f"   계좌당 평균 종목수: {total_stocks/len(asset_distribution):.1f}개")

    def analyze_sector_concentration(self):
        """섹터 집중도 분석 (종목명 기반 간단 분류)"""
        holdings = self.session.query(Holding)\
            .filter(Holding.quantity > 0)\
            .order_by(Holding.evaluation_amount.desc())\
            .all()

        if not holdings:
            print("❌ 보유종목 데이터가 없습니다.")
            return

        # 간단한 섹터 분류 (종목명 기반)
        sector_mapping = {
            '삼성': 'IT/전자',
            'SK': 'IT/에너지',
            'LG': 'IT/화학',
            '현대': '자동차',
            '카카오': 'IT/플랫폼',
            '네이버': 'IT/플랫폼',
            '포스코': '철강',
            '신한': '금융',
            '하나': '금융',
            'KB': '금융',
            '기아': '자동차',
            '셀트리온': '바이오',
            '바이오': '바이오',
            '제약': '제약',
            '코스닥': '기타'
        }

        sector_stats = {}
        total_value = sum(h.evaluation_amount or 0 for h in holdings)

        for holding in holdings:
            sector = '기타'
            for keyword, mapped_sector in sector_mapping.items():
                if keyword in holding.name:
                    sector = mapped_sector
                    break

            if sector not in sector_stats:
                sector_stats[sector] = {'value': 0, 'count': 0, 'holdings': []}

            sector_stats[sector]['value'] += holding.evaluation_amount or 0
            sector_stats[sector]['count'] += 1
            sector_stats[sector]['holdings'].append(holding.name)

        print("=" * 80)
        print("🏭 섹터별 집중도 분석 (추정)")
        print("=" * 80)

        data = []
        for sector, stats in sorted(sector_stats.items(), key=lambda x: x[1]['value'], reverse=True):
            percentage = (stats['value'] / total_value * 100) if total_value > 0 else 0
            data.append([
                sector,
                f"{stats['value']:,.0f}",
                f"{stats['count']}",
                f"{percentage:.1f}%"
            ])

        print(tabulate(data,
                      headers=["섹터", "가치", "종목수", "비중"],
                      tablefmt="grid"))

    def analyze_trading_patterns(self, days=30):
        """거래 패턴 분석"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # 일별 거래 통계
        daily_stats = self.session.query(
            Transaction.transaction_date,
            func.count(Transaction.id).label('total_count'),
            func.sum(func.case([(Transaction.transaction_type == 'BUY', 1)], else_=0)).label('buy_count'),
            func.sum(func.case([(Transaction.transaction_type == 'SELL', 1)], else_=0)).label('sell_count'),
            func.sum(Transaction.amount).label('total_amount')
        ).filter(
            and_(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date
            )
        ).group_by(Transaction.transaction_date)\
         .order_by(Transaction.transaction_date.desc())\
         .limit(10).all()

        print("=" * 100)
        print(f"📈 최근 {days}일 거래 패턴 분석")
        print("=" * 100)

        if not daily_stats:
            print("❌ 거래 데이터가 없습니다.")
            return

        data = []
        for stat in daily_stats:
            data.append([
                stat.transaction_date.strftime("%Y-%m-%d"),
                f"{stat.total_count}",
                f"{stat.buy_count}",
                f"{stat.sell_count}",
                f"{stat.total_amount:,.0f}"
            ])

        print(tabulate(data,
                      headers=["날짜", "총거래", "매수", "매도", "거래금액"],
                      tablefmt="grid"))

        # 전체 통계
        total_transactions = sum(s.total_count for s in daily_stats)
        total_amount = sum(s.total_amount for s in daily_stats)
        avg_daily_transactions = total_transactions / len(daily_stats) if daily_stats else 0

        print(f"\n📊 거래 요약:")
        print(f"   총 거래수: {total_transactions}건")
        print(f"   총 거래금액: {total_amount:,.0f}원")
        print(f"   일평균 거래: {avg_daily_transactions:.1f}건")

    def analyze_performance_trends(self, days=30):
        """수익률 추이 분석"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # 일별 잔고 추이
        balance_trends = self.session.query(
            DailyBalance.balance_date,
            func.sum(DailyBalance.total_balance).label('total_balance'),
            func.sum(DailyBalance.profit_loss).label('total_profit_loss'),
            func.avg(DailyBalance.profit_loss_rate).label('avg_profit_rate')
        ).filter(
            and_(
                DailyBalance.balance_date >= start_date,
                DailyBalance.balance_date <= end_date
            )
        ).group_by(DailyBalance.balance_date)\
         .order_by(DailyBalance.balance_date.desc())\
         .limit(10).all()

        print("=" * 100)
        print(f"📊 최근 {days}일 수익률 추이")
        print("=" * 100)

        if not balance_trends:
            print("❌ 잔고 데이터가 없습니다.")
            return

        data = []
        for trend in balance_trends:
            data.append([
                trend.balance_date.strftime("%Y-%m-%d"),
                f"{trend.total_balance:,.0f}" if trend.total_balance else "0",
                f"{trend.total_profit_loss:,.0f}" if trend.total_profit_loss else "0",
                f"{trend.avg_profit_rate:.2f}%" if trend.avg_profit_rate else "0.00%"
            ])

        print(tabulate(data,
                      headers=["날짜", "총잔고", "손익", "평균수익률"],
                      tablefmt="grid"))

        # 수익률 변화 계산
        if len(balance_trends) >= 2:
            latest = balance_trends[0]
            previous = balance_trends[1]

            balance_change = (latest.total_balance or 0) - (previous.total_balance or 0)
            profit_change = (latest.total_profit_loss or 0) - (previous.total_profit_loss or 0)

            print(f"\n📈 전일 대비 변화:")
            print(f"   잔고 변화: {balance_change:+,.0f}원")
            print(f"   손익 변화: {profit_change:+,.0f}원")

    def analyze_top_performers(self, limit=10):
        """상위/하위 수익 종목 분석"""
        holdings = self.session.query(Holding, Account, Broker)\
            .join(Account).join(Broker)\
            .filter(Holding.quantity > 0)\
            .order_by(Holding.profit_loss_rate.desc())\
            .all()

        if not holdings:
            print("❌ 보유종목 데이터가 없습니다.")
            return

        print("=" * 120)
        print(f"🏆 TOP {limit} 수익 종목")
        print("=" * 120)

        # 상위 종목
        top_performers = holdings[:limit]
        data = []
        for holding, account, broker in top_performers:
            data.append([
                holding.symbol,
                holding.name,
                f"{holding.evaluation_amount:,.0f}",
                f"{holding.profit_loss:+,.0f}",
                f"{holding.profit_loss_rate:+.2f}%"
            ])

        print(tabulate(data,
                      headers=["종목코드", "종목명", "평가액", "손익", "수익률"],
                      tablefmt="grid"))

        # 하위 종목
        print(f"\n📉 BOTTOM {limit} 수익 종목")
        print("=" * 120)

        bottom_performers = holdings[-limit:]
        data = []
        for holding, account, broker in bottom_performers:
            data.append([
                holding.symbol,
                holding.name,
                f"{holding.evaluation_amount:,.0f}",
                f"{holding.profit_loss:+,.0f}",
                f"{holding.profit_loss_rate:+.2f}%"
            ])

        print(tabulate(data,
                      headers=["종목코드", "종목명", "평가액", "손익", "수익률"],
                      tablefmt="grid"))

    def analyze_risk_metrics(self):
        """위험 지표 분석"""
        # 포트폴리오 집중도
        total_value = self.session.query(func.sum(Holding.evaluation_amount))\
            .filter(Holding.quantity > 0).scalar() or 0

        if total_value == 0:
            print("❌ 포트폴리오 데이터가 없습니다.")
            return

        # 상위 종목 집중도
        top_holdings = self.session.query(Holding)\
            .filter(Holding.quantity > 0)\
            .order_by(Holding.evaluation_amount.desc())\
            .limit(5).all()

        print("=" * 80)
        print("⚠️ 위험 지표 분석")
        print("=" * 80)

        top_5_value = sum(h.evaluation_amount or 0 for h in top_holdings)
        concentration_ratio = (top_5_value / total_value * 100) if total_value > 0 else 0

        print(f"📊 포트폴리오 집중도:")
        print(f"   상위 5종목 비중: {concentration_ratio:.1f}%")

        if concentration_ratio > 70:
            print("   🔴 위험도: 높음 (집중도 과다)")
        elif concentration_ratio > 50:
            print("   🟡 위험도: 보통 (집중도 높음)")
        else:
            print("   🟢 위험도: 낮음 (분산 양호)")

        # 마이너스 종목 비율
        total_holdings = self.session.query(func.count(Holding.id))\
            .filter(Holding.quantity > 0).scalar() or 0

        negative_holdings = self.session.query(func.count(Holding.id))\
            .filter(and_(Holding.quantity > 0, Holding.profit_loss < 0)).scalar() or 0

        negative_ratio = (negative_holdings / total_holdings * 100) if total_holdings > 0 else 0

        print(f"\n📉 손실 종목 비율:")
        print(f"   손실 종목: {negative_holdings}/{total_holdings} ({negative_ratio:.1f}%)")

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python db_analysis.py [분석유형]")
        print("\n사용 가능한 분석:")
        print("  portfolio     - 포트폴리오 분포 분석")
        print("  sector        - 섹터 집중도 분석")
        print("  trading       - 거래 패턴 분석")
        print("  performance   - 수익률 추이 분석")
        print("  top           - 상위/하위 수익 종목")
        print("  risk          - 위험 지표 분석")
        print("  all           - 전체 분석 실행")
        return

    analysis_type = sys.argv[1].lower()
    analyzer = DatabaseAnalyzer()

    try:
        if analysis_type == "portfolio":
            analyzer.analyze_portfolio_distribution()
        elif analysis_type == "sector":
            analyzer.analyze_sector_concentration()
        elif analysis_type == "trading":
            analyzer.analyze_trading_patterns()
        elif analysis_type == "performance":
            analyzer.analyze_performance_trends()
        elif analysis_type == "top":
            analyzer.analyze_top_performers()
        elif analysis_type == "risk":
            analyzer.analyze_risk_metrics()
        elif analysis_type == "all":
            print("🔍 종합 분석 실행")
            print("\n")
            analyzer.analyze_portfolio_distribution()
            print("\n")
            analyzer.analyze_sector_concentration()
            print("\n")
            analyzer.analyze_trading_patterns()
            print("\n")
            analyzer.analyze_performance_trends()
            print("\n")
            analyzer.analyze_top_performers()
            print("\n")
            analyzer.analyze_risk_metrics()
        else:
            print(f"❌ 알 수 없는 분석 유형: {analysis_type}")

    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {str(e)}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()