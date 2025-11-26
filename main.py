import os
import time
from tqdm import tqdm
from dotenv import load_dotenv
from call_login_api import check_api_status, login
from logger_config import setup_logger
from import_user import import_user_from_hireme
from query_user_table_sqlalchemy import (
    create_database_engine,
    query_user_table_to_dataframe
)

# 載入 .env 檔案
load_dotenv()

# 設定 logger
logger = setup_logger("main")


def load_database_config():
    """讀取資料庫設定"""
    return {
        "server": os.getenv("DB_SERVER"),
        "database": os.getenv("DB_DATABASE"),
        "user_id": os.getenv("DB_USER_ID"),
        "password": os.getenv("DB_PASSWORD"),
        "trust_server_certificate": os.getenv("DB_TRUST_SERVER_CERTIFICATE", "true").lower() == "true",
        "multiple_active_result_sets": os.getenv("DB_MULTIPLE_ACTIVE_RESULT_SETS", "true").lower() == "true"
    }


def load_api_config():
    """讀取 API 設定"""
    return {
        "base_url": os.getenv("API_BASE_URL", "https://localhost:7013").strip(),
        "tenant": os.getenv("API_TENANT") or None,
        "access_token": os.getenv("API_ACCESS_TOKEN", ""),
        "client_id": os.getenv("API_CLIENT_ID"),
        "client_secret": os.getenv("API_CLIENT_SECRET"),
        "password": os.getenv("API_PASSWORD")
    }


def import_users(login_names_list, api_config, pbar, total_users):
    """匯入員工資料"""
    success_count = 0
    fail_count = 0

    for index, login_name in enumerate(login_names_list):
        display_name = login_name[:15] + "..." if len(login_name) > 15 else login_name
        pbar.set_description(f"匯入: {display_name}")

        try:
            result = import_user_from_hireme(
                base_url=api_config["base_url"],
                loginname=login_name,
                access_token=api_config["access_token"],
                tenant=api_config["tenant"]
            )
            success_count += 1
            # 每100個成功或最後一個才輸出到控制台，避免刷屏
            if (index + 1) % 100 == 0 or (index + 1) == total_users:
                tqdm.write(f"[{index + 1}/{total_users}] ✓ {login_name} 匯入成功")
            logger.info(f"[{index + 1}/{total_users}] 員工 {login_name} 匯入成功: {result}")
        except Exception as e:
            fail_count += 1
            logger.error(f"[{index + 1}/{total_users}] 員工 {login_name} 匯入失敗: {str(e)}", exc_info=True)
        finally:
            pbar.set_postfix({
                "成功": success_count,
                "失敗": fail_count,
                "成功率": f"{success_count / (index + 1) * 100:.2f}%" if (index + 1) > 0 else "0.00%"
            })
            pbar.update(1)
            # 添加請求間隔，避免 API 過載
            if index < total_users - 1:
                time.sleep(0.5)

    return success_count, fail_count


def test_user_login(login_names_list, api_config):
    """測試使用者登入"""
    login_success = []
    login_fail = []

    tqdm.write("\n開始測試使用者登入...")
    for login_name in login_names_list:
        try:
            result = login(
                base_url=api_config["base_url"],
                client_id=api_config["client_id"],
                client_secret=api_config["client_secret"],
                username=login_name,
                password=api_config["password"],
                tenant=api_config["tenant"]
            )
            if result and "access_token" in result:
                login_success.append(login_name)
            else:
                login_fail.append(login_name)
        except Exception as e:
            login_fail.append(login_name)
            logger.debug(f"使用者 {login_name} 登入測試失敗: {str(e)}")

    return login_success, login_fail


def main():
    """主程式"""
    engine = None
    try:
        # 讀取設定
        db_config = load_database_config()
        api_config = load_api_config()

        # 連接資料庫
        engine = create_database_engine(
            server=db_config["server"],
            database=db_config["database"],
            user_id=db_config["user_id"],
            password=db_config["password"],
            trust_server_certificate=db_config["trust_server_certificate"],
            multiple_active_result_sets=db_config["multiple_active_result_sets"]
        )

        # 查詢 user 表資料
        user_dataframe = query_user_table_to_dataframe(engine, table_name="user")
        logger.info(f"從資料庫獲取 {len(user_dataframe)} 筆使用者資料")

        # 檢查 API 狀態
        tqdm.write("正在檢查 API 狀態...")
        api_status = check_api_status(base_url=api_config["base_url"])
        if not api_status:
            logger.error("API 狀態檢查失敗，請確認 API 服務是否運行且可訪問")
            tqdm.write("API 狀態檢查失敗，請確認 API 服務是否運行且可訪問")
            return

        # 驗證 LoginName 欄位
        if "LoginName" not in user_dataframe.columns:
            logger.error("user 表中沒有 LoginName 欄位")
            logger.info(f"可用欄位: {list(user_dataframe.columns)}")
            return

        # 獲取所有 LoginName
        login_names_list = user_dataframe["LoginName"].tolist()
        total_users = len(login_names_list)

        if total_users == 0:
            logger.warning("沒有找到任何使用者")
            return

        # 開始匯入員工資料
        logger.info(f"開始匯入 {total_users} 個員工資料")
        tqdm.write(f"\n{'='*60}")
        tqdm.write(f"開始匯入 {total_users} 個員工資料...")
        tqdm.write(f"{'='*60}\n")

        with tqdm(
            total=total_users,
            desc="匯入員工資料",
            unit="員工",
            ncols=120,
            mininterval=0.05,
            miniters=1,
            file=None,
            dynamic_ncols=True,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}'
        ) as pbar:
            success_count, fail_count = import_users(login_names_list, api_config, pbar, total_users)

        # 測試使用者登入
        login_success, login_fail = test_user_login(login_names_list, api_config)

        # 輸出登入測試結果
        tqdm.write("\n" + "="*60)
        tqdm.write("登入測試完成：")
        tqdm.write(f"成功 ({len(login_success)}): {login_success[:10]}{'...' if len(login_success) > 10 else ''}")
        tqdm.write(f"失敗 ({len(login_fail)}): {login_fail[:10]}{'...' if len(login_fail) > 10 else ''}")
        tqdm.write("="*60)

        # 輸出最終統計
        final_success_rate = (success_count / total_users * 100) if total_users > 0 else 0.0
        final_msg = (
            f"\n{'='*60}\n"
            f"匯入完成！\n"
            f"總計: {total_users} 個員工\n"
            f"成功: {success_count} 個\n"
            f"失敗: {fail_count} 個\n"
            f"成功率: {final_success_rate:.2f}%\n"
            f"{'='*60}"
        )
        tqdm.write(final_msg)
        logger.info(final_msg)

    except Exception as e:
        logger.error(f"主程式發生錯誤: {e}", exc_info=True)
        tqdm.write(f"\n主程式發生錯誤: {e}")
    finally:
        # 關閉資料庫引擎
        if engine:
            engine.dispose()
            logger.info("資料庫引擎已關閉")
            tqdm.write("資料庫引擎已關閉")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"主程式發生錯誤: {e}", exc_info=True)
        print(f"\n主程式發生錯誤: {e}")
