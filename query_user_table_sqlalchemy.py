"""
使用 SQLAlchemy 查詢 SQL Server 資料庫中的 user 表資料
"""

import os
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from dotenv import load_dotenv
from logger_config import setup_logger

# 載入 .env 檔案
load_dotenv()

# 設定 logger
logger = setup_logger("query_user_table_sqlalchemy")


def create_database_engine(
    server: str,
    database: str,
    user_id: str,
    password: str,
    trust_server_certificate: bool = True,
    multiple_active_result_sets: bool = True,
    driver: str = "ODBC Driver 17 for SQL Server"
) -> Engine:
    """
    使用 SQLAlchemy 創建資料庫引擎

    Args:
        server: 伺服器位址
        database: 資料庫名稱
        user_id: 使用者 ID
        password: 密碼
        trust_server_certificate: 是否信任伺服器憑證
        multiple_active_result_sets: 是否允許多個活動結果集
        driver: ODBC Driver 名稱

    Returns:
        SQLAlchemy Engine 物件
    """
    # 構建連接字串 (使用 pyodbc)
    # URL 編碼特殊字元
    from urllib.parse import quote_plus
    encoded_password = quote_plus(password)

    connection_string = (
        f"mssql+pyodbc://{user_id}:{encoded_password}@{server}/{database}"
        f"?driver={quote_plus(driver)}"
        f"&TrustServerCertificate={'yes' if trust_server_certificate else 'no'}"
        f"&MultipleActiveResultSets={'yes' if multiple_active_result_sets else 'no'}"
    )

    try:
        engine = create_engine(
            connection_string,
            echo=False,  # 設為 True 可以看到 SQL 語句
            pool_pre_ping=True,  # 自動檢查連接是否有效
            pool_recycle=3600,  # 每小時回收連接
        )
        logger.info(f"成功創建資料庫引擎: {server}/{database}")
        return engine
    except Exception as e:
        logger.error(f"創建資料庫引擎時發生錯誤: {e}")
        raise


def get_session(engine: Engine) -> Session:
    """
    從引擎創建 Session

    Args:
        engine: SQLAlchemy Engine 物件

    Returns:
        SQLAlchemy Session 物件
    """
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def query_user_table(
    engine: Engine,
    table_name: str = "user",
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    使用 SQLAlchemy 查詢 user 表的所有資料

    Args:
        engine: SQLAlchemy Engine 物件
        table_name: 表名稱 (預設: "user")
        limit: 限制返回的記錄數 (可選)

    Returns:
        包含所有記錄的字典列表
    """
    query = f"SELECT * FROM [{table_name}]"
    if limit:
        query = f"SELECT TOP {limit} * FROM [{table_name}]"

    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()

            # 轉換為字典列表
            results = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                results.append(row_dict)

            logger.info(f"成功查詢到 {len(results)} 筆記錄")
            return results

    except SQLAlchemyError as e:
        logger.error(f"查詢資料時發生錯誤: {e}")
        raise


def query_user_table_to_dataframe(
    engine: Engine,
    table_name: str = "user",
    limit: Optional[int] = None
) -> pd.DataFrame:
    """
    使用 SQLAlchemy 查詢 user 表並返回 pandas DataFrame

    Args:
        engine: SQLAlchemy Engine 物件
        table_name: 表名稱 (預設: "user")
        limit: 限制返回的記錄數 (可選)

    Returns:
        pandas DataFrame
    """
    query = f"SELECT * FROM [{table_name}]"
    if limit:
        query = f"SELECT TOP {limit} * FROM [{table_name}]"

    try:
        df = pd.read_sql(query, engine)
        logger.info(f"成功查詢到 {len(df)} 筆記錄")
        return df
    except Exception as e:
        logger.error(f"查詢資料時發生錯誤: {e}")
        raise


def get_table_info(engine: Engine, table_name: str = "user") -> None:
    """
    使用 SQLAlchemy 顯示表的結構資訊

    Args:
        engine: SQLAlchemy Engine 物件
        table_name: 表名稱
    """
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)

        logger.info(f"表 '{table_name}' 的結構資訊:")
        logger.info("-" * 80)
        logger.info(f"{'欄位名稱':<30} {'資料型別':<20} {'可為空':<10} {'預設值':<20}")
        logger.info("-" * 80)

        for col in columns:
            col_name = col['name']
            data_type = str(col['type'])
            nullable = "YES" if col['nullable'] else "NO"
            default = str(col.get('default', 'N/A'))
            logger.info(f"{col_name:<30} {data_type:<20} {nullable:<10} {default:<20}")

    except Exception as e:
        logger.error(f"查詢表結構時發生錯誤: {e}")


def query_with_sql(engine: Engine, sql: str) -> pd.DataFrame:
    """
    執行自訂 SQL 查詢並返回 DataFrame

    Args:
        engine: SQLAlchemy Engine 物件
        sql: SQL 查詢語句

    Returns:
        pandas DataFrame
    """
    try:
        df = pd.read_sql(sql, engine)
        logger.info(f"成功執行 SQL 查詢，返回 {len(df)} 筆記錄")
        return df
    except Exception as e:
        logger.error(f"執行 SQL 查詢時發生錯誤: {e}")
        raise


if __name__ == "__main__":
    # 從 .env 檔案讀取資料庫連接參數
    SERVER = os.getenv("DB_SERVER", "192.168.1.109")
    DATABASE = os.getenv("DB_DATABASE", "HireMePlz")
    USER_ID = os.getenv("DB_USER_ID", "alanRunnerMan")
    PASSWORD = os.getenv("DB_PASSWORD", "e93T1R7oKQhHt1vf")
    TRUST_SERVER_CERTIFICATE = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "true").lower() == "true"
    MULTIPLE_ACTIVE_RESULT_SETS = os.getenv("DB_MULTIPLE_ACTIVE_RESULT_SETS", "true").lower() == "true"

    engine = None

    try:
        # 創建資料庫引擎
        engine = create_database_engine(
            server=SERVER,
            database=DATABASE,
            user_id=USER_ID,
            password=PASSWORD,
            trust_server_certificate=TRUST_SERVER_CERTIFICATE,
            multiple_active_result_sets=MULTIPLE_ACTIVE_RESULT_SETS
        )

        # 顯示表結構資訊
        get_table_info(engine, table_name="user")

        # 查詢 user 表的所有資料
        logger.info("正在查詢 user 表資料...")
        user_data = query_user_table(engine, table_name="user")

        # 顯示前幾筆資料
        if user_data:
            logger.info(f"前 5 筆資料:")
            logger.info("=" * 80)
            for i, record in enumerate(user_data[:5], 1):
                logger.info(f"記錄 {i}:")
                for key, value in record.items():
                    logger.info(f"  {key}: {value}")

            if len(user_data) > 5:
                logger.info(f"... 還有 {len(user_data) - 5} 筆記錄")

        else:
            logger.warning("user 表中沒有資料")

        # 使用 pandas DataFrame 方式查詢
        logger.info("使用 pandas DataFrame 查詢...")
        df = query_user_table_to_dataframe(engine, table_name="user")
        logger.info("DataFrame 資訊:")
        logger.info(f"\n{df.info()}")
        logger.info("前 5 筆資料:")
        logger.info(f"\n{df.head()}")

    except Exception as e:
        logger.error(f"發生錯誤: {e}", exc_info=True)

    finally:
        # 關閉引擎
        if engine:
            engine.dispose()
            logger.info("資料庫引擎已關閉")

