"""
新增使用者 API
POST /api/app/users/import-from-hireme

請求格式：
{
  "LoginName": "jebytestforRegister789@jbjob.com.tw"
}
"""

import os
import time
import json
import requests
import urllib3
from typing import Optional, Dict, Any, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from logger_config import setup_logger

# 禁用 SSL 警告（僅用於開發環境）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入 .env 檔案
load_dotenv()

# 設定 logger
logger = setup_logger("import_user")


def import_user_from_hireme(
    base_url: str,
    loginname: str,
    access_token: str ,
    tenant: Optional[str] = None,
    x_requested_with: str = "XMLHttpRequest",
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Dict[Any, Any]:
    """
    從 HireMe 匯入使用者

    Args:
        base_url: API 基礎 URL (例如: https://api.example.com)
        loginname: 使用者登入名稱 (例如: st_st53@msn.com)
        access_token: OAuth2 access token（可選，如果提供則加入 Authorization header）
        tenant: 租戶名稱 (可選)
        x_requested_with: X-Requested-With header 值 (預設: "XMLHttpRequest")
        timeout: 請求超時時間（秒，預設: 30）
        max_retries: 最大重試次數（預設: 3）
        retry_delay: 重試延遲時間（秒，預設: 1.0）

    Returns:
        API 回應的 JSON 資料
    """
    # 構建完整的 API URL（去除空格和尾部斜線）
    base_url = base_url.strip()
    url = f"{base_url.rstrip('/')}/membership/api/app/users/import-from-hireme"

    # 準備請求 headers
    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": x_requested_with
    }

    # 如果有提供 access_token，加入 Authorization header
    if access_token and access_token.strip():
        headers["Authorization"] = f"Bearer {access_token.strip()}"

    # 如果有提供 tenant，加入 header
    if tenant:
        headers["__tenant"] = tenant

    # 準備請求 body (JSON 格式)
    json_data = {
        "LoginName": loginname
    }

    # 創建 Session 並設定重試策略
    session = requests.Session()

    # 如果是 localhost 或 127.0.0.1，禁用 SSL 驗證（開發環境）
    if 'localhost' in base_url.lower() or '127.0.0.1' in base_url:
        session.verify = False
        logger.debug(f"已禁用 SSL 驗證（開發環境）: {base_url}")

    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=retry_delay,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        logger.debug(f"發送 POST 請求到: {url}, LoginName: {loginname}")
        response = session.post(url, headers=headers, json=json_data, timeout=timeout)
        response.raise_for_status()
        logger.info(f"成功匯入使用者 - loginname: {loginname}")
        return response.json()

    except requests.exceptions.Timeout:
        logger.error(f"請求超時 - loginname: {loginname}, timeout: {timeout}秒")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.error(f"連接錯誤 - loginname: {loginname}, 錯誤: {e}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP 錯誤 - loginname: {loginname}, 狀態碼: {e.response.status_code if e.response else 'N/A'}")
        if e.response is not None:
            logger.error(f"回應內容: {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"請求錯誤 - loginname: {loginname}, 錯誤: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"回應內容: {e.response.text}")
        raise
    finally:
        session.close()


def import_users_batch(
    base_url: str,
    loginnames: List[str],
    access_token: str,
    tenant: Optional[str] = None,
    delay_between_requests: float = 0.5,
    timeout: int = 30,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    批次匯入多個使用者

    Args:
        base_url: API 基礎 URL
        loginnames: 使用者登入名稱列表
        access_token: OAuth2 access token
        tenant: 租戶名稱 (可選)
        delay_between_requests: 請求之間的延遲時間（秒，預設: 0.5）
        timeout: 請求超時時間（秒，預設: 30）
        max_retries: 最大重試次數（預設: 3）

    Returns:
        包含成功和失敗統計的字典
    """
    results = {
        "total": len(loginnames),
        "success": [],
        "failed": [],
        "success_count": 0,
        "failed_count": 0
    }

    for loginname in loginnames:
        try:
            result = import_user_from_hireme(
                base_url=base_url,
                loginname=loginname,
                access_token=access_token,
                tenant=tenant,
                timeout=timeout,
                max_retries=max_retries
            )
            results["success"].append({"loginname": loginname, "result": result})
            results["success_count"] += 1
            logger.info(f"✓ 成功匯入使用者: {loginname}")

        except Exception as e:
            results["failed"].append({"loginname": loginname, "error": str(e)})
            results["failed_count"] += 1
            logger.error(f"✗ 匯入使用者失敗: {loginname}, 錯誤: {e}")

        # 添加請求間隔
        if delay_between_requests > 0:
            time.sleep(delay_between_requests)

    return results


if __name__ == "__main__":
    # 從 .env 檔案讀取設定
    BASE_URL = "https://localhost:7013" #os.getenv("API_BASE_URL", "")
    LOGINNAME = "st_st53@msn.com"
    TENANT = None

    try:
        # 匯入單個使用者
        result = import_user_from_hireme(
            base_url=BASE_URL,
            loginname=LOGINNAME,
            access_token="",
            tenant=TENANT
        )

        logger.info("匯入使用者成功！")
        logger.info(f"回應資料: {result}")

    except Exception as e:
        logger.error(f"發生錯誤: {e}", exc_info=True)
