"""
使用 SQLAlchemy 版本的 main.py
"""

import os
from dotenv import load_dotenv
from logger_config import setup_logger
from query_user_table_sqlalchemy import (
    create_database_engine,
    query_user_table_to_dataframe
)

# 載入 .env 檔案
load_dotenv()

# 設定 logger
logger = setup_logger("main_sqlalchemy")

if __name__ == "__main__":
    # 將User table 的LoginName 取出來

    # 讀取.env 中的DB_SERVER, DB_DATABASE, DB_USER_ID, DB_PASSWORD
    db_server = os.getenv("DB_SERVER")
    db_database = os.getenv("DB_DATABASE")
    db_user_id = os.getenv("DB_USER_ID")
    db_password = os.getenv("DB_PASSWORD")
    trust_server_certificate = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "true").lower() == "true"
    multiple_active_result_sets = os.getenv("DB_MULTIPLE_ACTIVE_RESULT_SETS", "true").lower() == "true"

    engine = None

    try:
        # 創建資料庫引擎
        engine = create_database_engine(
            server=db_server,
            database=db_database,
            user_id=db_user_id,
            password=db_password,
            trust_server_certificate=trust_server_certificate,
            multiple_active_result_sets=multiple_active_result_sets
        )

        # 查詢 user 表資料
        user_dataframe = query_user_table_to_dataframe(engine, table_name="user")

        # 輸出所有 LoginName
        if "LoginName" in user_dataframe.columns:
            logger.info("User table 的 LoginName 列表:")
            for login_name in user_dataframe["LoginName"]:
                logger.info(login_name)
        else:
            logger.warning("user 表中沒有 LoginName 欄位")
            logger.info(f"可用欄位: {list(user_dataframe.columns)}")

    except Exception as e:
        logger.error(f"發生錯誤: {e}", exc_info=True)

    finally:
        # 關閉引擎
        if engine:
            engine.dispose()
            logger.info("資料庫引擎已關閉")

