import os
import time
from tqdm import tqdm
from dotenv import load_dotenv
from call_login_api import login
from call_login_api import check_api_status
from logger_config import setup_logger
from query_user_table_sqlalchemy import (
    create_database_engine,
    query_user_table_to_dataframe
)

# 載入 .env 檔案
load_dotenv()

# 設定 logger
logger = setup_logger("main")

def main():
    # 將User table 的LoginName 取出來

    # 讀取.env 中的DB_SERVER, DB_DATABASE, DB_USER_ID, DB_PASSWORD
    db_server = os.getenv("DB_SERVER")
    db_database = os.getenv("DB_DATABASE")
    db_user_id = os.getenv("DB_USER_ID")
    db_password = os.getenv("DB_PASSWORD")
    trust_server_certificate = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "true").lower() == "true"
    multiple_active_result_sets = os.getenv("DB_MULTIPLE_ACTIVE_RESULT_SETS", "true").lower() == "true"

    engine = None
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
    logger.info(user_dataframe)

    # # 輸出所有 LoginName
    # if "LoginName" in user_dataframe.columns:
    #     logger.info("User table 的 LoginName 列表:")
    #     for index, row in user_dataframe.iterrows():
    #         login_name = row["LoginName"]
    #         logger.info(f"LoginName: {login_name}")
    # else:
    #     logger.warning("user 表中沒有 LoginName 欄位")
    #     logger.info(f"可用欄位: {list(user_dataframe.columns)}")






 # 先登入一個測試看看


    response = check_api_status(base_url="https://localhost:7013")
    if not response:
        logger.error("API 狀態檢查失敗")
        return None


    response = login(
        base_url="https://localhost:7013",
        client_id="Public.JbJobMembership_Swagger",
        client_secret="",
        username="0985468598",
        password="jebydev@6h4Lk6td4Jkj",
    )
    if not response:
        logger.error("登入失敗")
        return None
    logger.info(response)

    # 開始登入所有的使用者
    # 確保 LoginName 欄位存在
    if "LoginName" not in user_dataframe.columns:
        logger.error("user 表中沒有 LoginName 欄位")
        logger.info(f"可用欄位: {list(user_dataframe.columns)}")
        return None

    # 獲取所有 LoginName
    login_names_list = user_dataframe["LoginName"].tolist()
    total_users = len(login_names_list)

    if total_users == 0:
        logger.warning("沒有找到任何使用者")
        return None

    logger.info(f"開始處理 {total_users} 個使用者登入")
    success_count = 0
    fail_count = 0

    # 使用 tqdm 顯示進度條
    # 設定參數確保進度條完整顯示
    with tqdm(
        total=total_users,
        desc="處理使用者登入",
        unit="用戶",
        ncols=120,
        mininterval=0.05,  # 最小更新間隔（更頻繁更新）
        miniters=1,  # 最小迭代次數
        file=None,  # 輸出到 stdout
        dynamic_ncols=True,  # 動態調整寬度
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}'  # 自訂格式
    ) as pbar:
        # 使用 enumerate 確保索引正確
        for current_index, login_name in enumerate(login_names_list, start=1):
            # 更新進度條描述（限制長度避免過長）
            display_name = login_name[:15] + "..." if len(login_name) > 15 else login_name
            pbar.set_description(f"處理: {display_name}")

            try:
                response = login(
                    base_url="https://localhost:7013",
                    client_id="Public.JbJobMembership_Swagger",
                    client_secret="",
                    username=login_name,
                    password="jebydev@6h4Lk6td4Jkj",
                )
                success_count += 1
                # 使用 tqdm.write() 輸出日誌，避免干擾進度條
                # 只在每 100 個或失敗時顯示，減少輸出
                if current_index % 100 == 0 or current_index == total_users:
                    tqdm.write(f"[{current_index}/{total_users}] ✓ {login_name} 登入成功")
                logger.info(f"[{current_index}/{total_users}] 使用者 {login_name} 登入成功")
                pbar.set_postfix({
                    "成功": success_count,
                    "失敗": fail_count,
                    "成功率": f"{(success_count/current_index*100):.1f}%"
                })
            except Exception as e:
                fail_count += 1
                # 使用 tqdm.write() 輸出錯誤，避免干擾進度條
                error_msg = str(e)[:80]  # 限制錯誤訊息長度
                tqdm.write(f"[{current_index}/{total_users}] ✗ {login_name} 登入失敗: {error_msg}")
                logger.error(f"[{current_index}/{total_users}] 使用者 {login_name} 登入失敗: {str(e)}")
                pbar.set_postfix({
                    "成功": success_count,
                    "失敗": fail_count,
                    "成功率": f"{(success_count/current_index*100):.1f}%"
                })
            finally:
                # 更新進度條（確保每次迭代都更新）
                pbar.update(1)

                # 添加請求間隔，避免請求過於頻繁
                if current_index < total_users:  # 最後一個不需要延遲
                    time.sleep(0.5)  # 每次請求間隔0.5秒

    # 處理完成後輸出最終統計
    success_rate = (success_count / total_users * 100) if total_users > 0 else 0
    final_msg = f"\n{'='*60}\n處理完成！\n總計: {total_users} 個使用者\n成功: {success_count} 個\n失敗: {fail_count} 個\n成功率: {success_rate:.2f}%\n{'='*60}"
    print(final_msg)
    logger.info(final_msg)


if __name__ == "__main__":
    main()
