"""
呼叫登入 API - 前台
使用 OAuth2/OIDC password grant type
"""

import os
import time

import requests
import urllib3
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from logger_config import setup_logger

# 禁用 SSL 警告（僅用於開發環境）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入 .env 檔案
load_dotenv()

# 設定 logger
logger = setup_logger("call_login_api")


def login(
    base_url: str,
    client_id: str,
    client_secret: str,
    username: str,
    password: str,
    scope: str = "offline_access JbJobMembership",
    tenant: Optional[str] = None,
    x_requested_with: str = "XMLHttpRequest",
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Dict[Any, Any]:
    """
    呼叫登入 API（帶重試機制）

    Args:
        base_url: API 基礎 URL (例如: https://api.example.com)
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        username: 使用者名稱 (例如: 091011111111)
        password: 使用者密碼
        scope: OAuth2 scope (預設: "offline_access JbJobMembership")
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
    url = f"{base_url.rstrip('/')}/membership/connect/token"

    # 準備請求 headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": x_requested_with
    }

    # 如果有提供 tenant，加入 header
    if tenant:
        headers["__tenant"] = tenant

    # 準備請求 body (form-urlencoded)
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": scope
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
        logger.debug(f"發送 POST 請求到: {url}, username: {username}")
        response = session.post(url, headers=headers, data=data, timeout=timeout)
        response.raise_for_status()
        logger.info(f"API 請求成功 - username: {username}")
        return response.json()

    except requests.exceptions.Timeout:
        logger.error(f"請求超時 - username: {username}, timeout: {timeout}秒")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.error(f"連接錯誤 - username: {username}, 錯誤: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"請求錯誤 - username: {username}, 錯誤: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"回應內容: {e.response.text}")
        raise
    finally:
        session.close()

# 確認API是否可以用
def check_api_status(base_url: str) -> Optional[Dict[Any, Any]]:
    """
    確認API是否可以用

    Args:
        base_url: API 基礎 URL

    Returns:
        API 回應的 JSON 資料，如果失敗則返回 None
    """
    # 構建完整的 API URL（去除空格和尾部斜線）
    base_url = base_url.strip()
    url = f"{base_url.rstrip('/')}/membership/.well-known/openid-configuration"

    # 創建 Session
    session = requests.Session()

    # 如果是 localhost 或 127.0.0.1，禁用 SSL 驗證（開發環境）
    if 'localhost' in base_url.lower() or '127.0.0.1' in base_url:
        session.verify = False
        logger.debug(f"已禁用 SSL 驗證（開發環境）: {base_url}")

    try:
        logger.debug(f"檢查 API 狀態: {url}")
        response = session.get(url, timeout=10)
        response.raise_for_status()
        result = response.json()
        logger.info(f"API 狀態檢查成功: {url}")
        return result
    except requests.exceptions.SSLError as e:
        logger.error(f"SSL 錯誤 - 確認API是否可以用失敗: {e}")
        logger.info("嘗試禁用 SSL 驗證...")
        session.verify = False
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            result = response.json()
            logger.info(f"API 狀態檢查成功（已禁用 SSL 驗證）: {url}")
            return result
        except Exception as retry_e:
            logger.error(f"重試後仍然失敗: {retry_e}")
            return None
    except Exception as e:
        logger.error(f"確認API是否可以用失敗: {e}")
        return None
    finally:
        session.close()


def refresh_token(
    base_url: str,
    client_id: str,
    client_secret: str,
    refresh_token: str,
    tenant: Optional[str] = None,
    x_requested_with: str = "XMLHttpRequest",
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Dict[Any, Any]:
    """
    使用 refresh token 刷新 access token（帶重試機制）

    Args:
        base_url: API 基礎 URL
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        refresh_token: 之前獲得的 refresh token
        tenant: 租戶名稱 (可選)
        x_requested_with: X-Requested-With header 值
        timeout: 請求超時時間（秒，預設: 30）
        max_retries: 最大重試次數（預設: 3）
        retry_delay: 重試延遲時間（秒，預設: 1.0）

    Returns:
        API 回應的 JSON 資料
    """
    # 構建完整的 API URL（去除空格和尾部斜線）
    base_url = base_url.strip()
    url = f"{base_url.rstrip('/')}/membership/connect/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": x_requested_with
    }

    if tenant:
        headers["__tenant"] = tenant

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "offline_access JbJobMembership"
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
        logger.debug(f"發送 POST 請求到: {url}")
        response = session.post(url, headers=headers, data=data, timeout=timeout)
        response.raise_for_status()
        logger.info("Refresh token 請求成功")
        return response.json()

    except requests.exceptions.Timeout:
        logger.error(f"請求超時 - timeout: {timeout}秒")
        raise
    except requests.exceptions.ConnectionError as e:
        logger.error(f"連接錯誤: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"請求錯誤: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"回應內容: {e.response.text}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # 從 .env 檔案讀取 API 設定
    BASE_URL = os.getenv("API_BASE_URL", "http://192.168.1.109:5050")
    CLIENT_ID = os.getenv("API_CLIENT_ID", "Public.JbJobMembership_Swagger")
    CLIENT_SECRET = os.getenv("API_CLIENT_SECRET", "")
    USERNAME = os.getenv("API_USERNAME", "091011111111")
    PASSWORD = os.getenv("API_PASSWORD", "zQz6OTa95T6Q4Efy")
    TENANT = os.getenv("API_TENANT") or None  # 如果為空字串則設為 None

    logger.info("正在呼叫登入 API...")

    try:
        # 執行登入
        result = login(
            base_url=BASE_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            username=USERNAME,
            password=PASSWORD,
            tenant=TENANT
        )

        logger.info("登入成功！")
        logger.info(f"回應資料: {result}")

        # 如果有 refresh_token，可以儲存起來
        if "refresh_token" in result:
            refresh_token_value = result["refresh_token"]
            logger.info(f"Refresh Token: {refresh_token_value[:50]}...")

            # 範例：使用 refresh token 刷新 access token
            # logger.info("使用 refresh token 刷新 access token...")
            # new_tokens = refresh_token(
            #     base_url=BASE_URL,
            #     client_id=CLIENT_ID,
            #     client_secret=CLIENT_SECRET,
            #     refresh_token=refresh_token_value,
            #     tenant=TENANT
            # )
            # logger.info("刷新成功！")
            # logger.info(new_tokens)

    except Exception as e:
        logger.error(f"發生錯誤: {e}", exc_info=True)

