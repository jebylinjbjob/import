"""
查詢前台登入次數（按週統計）
User story: 我想要知道這個月有多少人登入過我的網站
並且讓我知道他的
"""

import os
import csv
from datetime import datetime, date
from typing import Optional, List, Tuple, Dict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
import logging

# 載入 .env 檔案
load_dotenv()

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("membership_db")

# 建立 Base 類別
Base = declarative_base()


# 定義 AbpAuditLogs 模型
class AbpAuditLogs(Base):
    """
    AbpAuditLogs 資料表模型
    """
    __tablename__ = 'AbpAuditLogs'
    __table_args__ = {'schema': 'dbo'}

    # 定義欄位（根據查詢需求，只定義必要的欄位）
    Id = Column(String, primary_key=True)
    ApplicationName = Column(String)
    Url = Column(String)
    HttpStatusCode = Column(Integer)
    ExecutionTime = Column(DateTime)
    # 其他欄位可以根據需要添加


def get_db_engine() -> Optional[Engine]:
    """
    創建資料庫引擎

    Returns:
        資料庫引擎物件，如果失敗則返回 None
    """
    try:
        # 從環境變數讀取資料庫連接資訊
        db_server = os.getenv("DB_SERVER")
        db_database = os.getenv("DB_DATABASE")
        db_username = os.getenv("DB_USER_ID")
        db_password = os.getenv("DB_PASSWORD")
        db_driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

        if not db_username or not db_password:
            logger.error("資料庫使用者名稱或密碼未設定，請檢查環境變數 DB_USERNAME 和 DB_PASSWORD")
            return None

        # 建立連接字串
        connection_string = (
            f"mssql+pyodbc://{db_username}:{db_password}@{db_server}/{db_database}"
            f"?driver={db_driver.replace(' ', '+')}"
            f"&autocommit=True"
        )

        engine = create_engine(
            connection_string,
            echo=False,
            pool_pre_ping=True
        )

        logger.info(f"成功創建資料庫引擎: {db_server}/{db_database}")
        return engine

    except Exception as e:
        logger.error(f"創建資料庫引擎失敗: {e}", exc_info=True)
        return None


def get_week_ranges() -> List[Tuple[str, date, date, str]]:
    """
    定義週的日期範圍（與 hireme.py 相同）

    Returns:
        週的列表，每個元素包含 (描述, 開始日期, 結束日期, 週標籤)
    """
    weeks = [
        ("2025/11月（第3週 11/17~11/23）", date(2025, 11, 17), date(2025, 11, 23), "2025-11-第3週"),
        ("2025/11月（第4週 11/24~11/30）", date(2025, 11, 24), date(2025, 11, 30), "2025-11-第4週"),
        ("2025/12月（第1週 12/1~12/7）", date(2025, 12, 1), date(2025, 12, 7), "2025-12-第1週"),
        ("2025/12月（第2週 12/8~12/14）", date(2025, 12, 8), date(2025, 12, 14), "2025-12-第2週"),
        ("2025/12月（第3週 12/15~12/21）", date(2025, 12, 15), date(2025, 12, 21), "2025-12-第3週"),
        ("2025/12月（第4週 12/22~12/28）", date(2025, 12, 22), date(2025, 12, 28), "2025-12-第4週"),
        ("2026/01月（第1週 12/29~1/4）", date(2025, 12, 29), date(2026, 1, 4), "2026-01-第1週"),
        ("2026/01月（第2週 1/5~1/11）", date(2026, 1, 5), date(2026, 1, 11), "2026-01-第2週"),
    ]
    return weeks


def query_weekly_login_count(engine: Engine, week_start: date, week_end: date) -> Optional[int]:
    """
    查詢指定週的前台登入次數（使用 ORM）

    Args:
        engine: 資料庫引擎
        week_start: 週開始日期
        week_end: 週結束日期

    Returns:
        該週的登入次數，如果失敗則返回 None
    """
    try:
        # 轉換為 datetime 物件
        start_datetime = datetime.combine(week_start, datetime.min.time())
        end_datetime = datetime.combine(week_end, datetime.max.time())

        # 建立 Session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        try:
            # 使用 ORM 查詢
            count = (
                session.query(func.count(AbpAuditLogs.Id))
                .filter(
                    AbpAuditLogs.ApplicationName == 'Public.JbJobMembership.HttpApi.Host',
                    AbpAuditLogs.Url.like('%/connect/token%'),
                    AbpAuditLogs.HttpStatusCode == 200,
                    AbpAuditLogs.ExecutionTime >= start_datetime,
                    AbpAuditLogs.ExecutionTime <= end_datetime
                )
                .scalar()
            )

            if count is not None:
                return count
            else:
                return 0

        finally:
            session.close()

    except Exception as e:
        logger.error(f"查詢週登入次數失敗: {e}", exc_info=True)
        return None


def query_total_login_count(engine: Engine) -> Optional[int]:
    """
    查詢總登入次數（11/17~1/11）

    Args:
        engine: 資料庫引擎

    Returns:
        總登入次數，如果失敗則返回 None
    """
    try:
        start_date = date(2025, 11, 17)
        end_date = date(2026, 1, 11)

        # 轉換為 datetime 物件
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())

        # 建立 Session
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        try:
            # 使用 ORM 查詢
            count = (
                session.query(func.count(AbpAuditLogs.Id))
                .filter(
                    AbpAuditLogs.ApplicationName == 'Public.JbJobMembership.HttpApi.Host',
                    (AbpAuditLogs.Url.like('%/connect/token%') | AbpAuditLogs.Url.like('%/api/app/line-login/token%')),
                    AbpAuditLogs.HttpStatusCode == 200,
                    AbpAuditLogs.ExecutionTime >= start_datetime,
                    AbpAuditLogs.ExecutionTime <= end_datetime
                )
                .scalar()
            )

            if count is not None:
                return count
            else:
                return 0

        finally:
            session.close()

    except Exception as e:
        logger.error(f"查詢總登入次數失敗: {e}", exc_info=True)
        return None


def generate_csv_report(week_counts: List[Dict], total_count: int, output_file: str = "membership_login_report.csv"):
    """
    產生 CSV 報告

    Args:
        week_counts: 各週統計列表
        total_count: 總登入次數
        output_file: 輸出檔案名稱
    """
    try:
        # 寫入 CSV
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # 寫入標題
            writer.writerow(['期間', '登入次數'])

            # 寫入總登入次數
            writer.writerow([f'總登入人數（11/17~1/11）', total_count])

            # 寫入各週統計
            for week_data in week_counts:
                writer.writerow([week_data['period'], week_data['count']])

        logger.info(f"CSV 報告已產生: {output_file}")

        # 輸出到控制台
        print(f"\n{'='*60}")
        print("前台登入次數統計報告")
        print(f"{'='*60}")
        print(f"總登入人數（11/17~1/11）：{total_count:,}")
        for week_data in week_counts:
            print(f"{week_data['period']}：{week_data['count']:,}")
        print(f"{'='*60}\n")
        print(f"報告已儲存至: {output_file}\n")

    except Exception as e:
        logger.error(f"產生 CSV 報告失敗: {e}", exc_info=True)


def main():
    """
    主函數
    """
    logger.info("開始查詢前台登入次數（按週統計）")

    # 創建資料庫引擎
    engine = get_db_engine()
    if not engine:
        logger.error("無法創建資料庫引擎，程式結束")
        return

    try:
        # 查詢總登入次數
        total_count = query_total_login_count(engine)
        if total_count is None:
            logger.error("查詢總登入次數失敗")
            return

        # 取得各週的統計
        weeks = get_week_ranges()
        week_counts = []

        for week_desc, week_start, week_end, week_label in weeks:
            count = query_weekly_login_count(engine, week_start, week_end)
            if count is not None:
                week_counts.append({
                    'period': week_desc,
                    'count': count
                })
                logger.info(f"{week_desc}: {count} 次")
            else:
                logger.warning(f"查詢 {week_desc} 失敗")

        # 產生 CSV 報告
        generate_csv_report(week_counts, total_count)

    finally:
        # 關閉資料庫引擎
        engine.dispose()
        logger.info("資料庫引擎已關閉")


if __name__ == "__main__":
    main()
