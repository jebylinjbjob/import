# JBHRIS Import 專案

這是一個用於連接 JBHRIS 系統的 Python 工具集，包含 API 登入、員工資料匯入和資料庫查詢功能。

## 功能說明

### 1. API 登入功能 (`call_login_api.py`)

- 使用 OAuth2/OIDC password grant type 進行登入
- 支援取得 access token 和 refresh token
- 支援使用 refresh token 刷新 access token
- 支援多租戶設定
- 自動重試機制和錯誤處理
- SSL 驗證處理（開發環境自動禁用）

### 2. 員工資料匯入功能 (`import_user.py`)

- 從 HireMe 系統匯入員工資料
- 支援批次匯入多個使用者
- 使用 JSON 格式請求（`{"LoginName": "xxx"}`）
- 支援 Bearer Token 認證（可選）
- 自動重試機制和錯誤處理
- 完整的日誌記錄

### 3. 資料庫查詢功能 (`query_user_table_sqlalchemy.py`)

- 使用 SQLAlchemy 連接 SQL Server 資料庫
- 查詢 user 表的資料
- 顯示表結構資訊
- 支援連接池管理，提高效能
- 支援自訂 SQL 查詢
- 與 pandas 完美整合

### 4. 主程式 (`main.py`)

- 整合資料庫查詢和員工匯入功能
- 批次處理所有員工資料匯入
- 自動測試使用者登入功能
- 使用 `tqdm` 顯示進度條
- 完整的統計報告

### 5. Logging 功能 (`logger_config.py`)

- 統一的日誌記錄系統
- 支援控制台和檔案輸出
- 自動輪轉日誌檔案（防止檔案過大）
- 日誌檔案名稱包含日期（格式：`YYYYMMDD`）
- 可透過環境變數設定日誌級別

## 環境需求

- Python 3.7 或更高版本
- SQL Server ODBC Driver 17 for SQL Server（或相容版本）

## 安裝步驟

### 1. 安裝 Python 依賴套件

```bash
pip install -r requirements.txt
```

### 2. 安裝 SQL Server ODBC Driver

**Windows:**

- 從 [Microsoft 官網](https://docs.microsoft.com/zh-tw/sql/connect/odbc/download-odbc-driver-for-sql-server) 下載並安裝 ODBC Driver 17 for SQL Server

**Linux:**

```bash
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

**macOS:**

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17 mssql-tools
```

## 環境設定

### 1. 複製環境變數範本

```bash
# 如果還沒有 .env 檔案，可以參考 .env.example
cp .env.example .env
```

### 2. 編輯 `.env` 檔案

編輯 `.env` 檔案，填入您的實際設定值：

```env
# 資料庫連線設定
DB_SERVER=192.168.1.109
DB_DATABASE=HireMePlz
DB_USER_ID=your_user_id
DB_PASSWORD=your_password
DB_TRUST_SERVER_CERTIFICATE=true
DB_MULTIPLE_ACTIVE_RESULT_SETS=true

# API 設定
API_BASE_URL=https://localhost:7013
API_CLIENT_ID=Public.JbJobMembership_Swagger
API_CLIENT_SECRET=your_client_secret
API_USERNAME=your_username
API_PASSWORD=your_password
API_TENANT=
API_ACCESS_TOKEN=  # 可選，如果需要 Bearer Token 認證

# Logging 設定（可選）
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**重要：** `.env` 檔案包含敏感資訊，請勿將其提交到版本控制系統。

### 3. Logging 設定

日誌檔案會自動儲存在 `logs/` 目錄下，檔案名稱包含日期（格式：`模組名稱_YYYYMMDD.log`）：

- `logs/main_YYYYMMDD.log` - 主程式相關日誌
- `logs/import_user_YYYYMMDD.log` - 員工匯入相關日誌
- `logs/call_login_api_YYYYMMDD.log` - API 登入相關日誌
- `logs/query_user_table_sqlalchemy_YYYYMMDD.log` - 資料庫查詢相關日誌

日誌級別可透過 `.env` 檔案中的 `LOG_LEVEL` 設定：

- `DEBUG` - 詳細除錯資訊
- `INFO` - 一般資訊（預設）
- `WARNING` - 警告訊息
- `ERROR` - 錯誤訊息
- `CRITICAL` - 嚴重錯誤

日誌檔案會自動輪轉，每個檔案最大 10MB，保留 5 個備份檔案。

## 使用方法

### API 登入

執行登入腳本：

```bash
python call_login_api.py
```

腳本會：

1. 從 `.env` 讀取 API 設定
2. 呼叫登入 API
3. 顯示登入結果和 token 資訊

**程式碼範例：**

```python
from call_login_api import login, refresh_token

# 登入
result = login(
    base_url="http://192.168.1.109:5050",
    client_id="Public.JbJobMembership_Swagger",
    client_secret="",
    username="091011111111",
    password="your_password"
)

# 使用 refresh token 刷新 access token
new_tokens = refresh_token(
    base_url="http://192.168.1.109:5050",
    client_id="Public.JbJobMembership_Swagger",
    client_secret="",
    refresh_token=result["refresh_token"]
)
```

### 資料庫查詢

執行資料庫查詢腳本：

```bash
python query_user_table_sqlalchemy.py
```

### 員工資料匯入

執行主程式進行批次匯入：

```bash
python main.py
```

主程式會執行以下步驟：

1. 連接資料庫並查詢所有使用者的 `LoginName`
2. 檢查 API 狀態
3. 批次匯入所有員工資料到系統
4. 測試所有使用者的登入功能
5. 顯示完整的統計報告

**程式碼範例：**

```python
from import_user import import_user_from_hireme, import_users_batch

# 匯入單個使用者
result = import_user_from_hireme(
    base_url="https://localhost:7013",
    loginname="user@example.com",
    access_token="",  # 可選，如果需要認證
    tenant=None  # 可選
)

# 批次匯入多個使用者
loginnames = ["user1@example.com", "user2@example.com"]
results = import_users_batch(
    base_url="https://localhost:7013",
    loginnames=loginnames,
    access_token="",
    delay_between_requests=0.5
)
```

### 查詢資料庫資料

執行資料庫查詢腳本：

```bash
python query_user_table_sqlalchemy.py
```

**程式碼範例：**

```python
from query_user_table_sqlalchemy import (
    create_database_engine,
    query_user_table,
    query_user_table_to_dataframe,
    query_with_sql,
    get_table_info
)

# 創建資料庫引擎
engine = create_database_engine(
    server="192.168.1.109",
    database="HireMePlz",
    user_id="alanRunnerMan",
    password="your_password"
)

# 查詢資料
user_data = query_user_table(engine, table_name="user")

# 或使用 pandas DataFrame
df = query_user_table_to_dataframe(engine, table_name="user")

# 執行自訂 SQL 查詢
custom_df = query_with_sql(engine, "SELECT * FROM [user] WHERE Id > 100")

# 顯示表結構
get_table_info(engine, table_name="user")

# 關閉引擎
engine.dispose()
```

**SQLAlchemy 的優勢：**

- 連接池管理，提高效能
- 更靈活的查詢方式
- 更好的錯誤處理
- 支援 ORM 模式（可選）
- 與 pandas 完美整合

## 專案結構

```text
.
├── README.md                          # 專案說明文件
├── requirements.txt                   # Python 依賴套件清單
├── .env                               # 環境變數設定（不提交到版本控制）
├── .env.example                       # 環境變數範本
├── .gitignore                         # Git 忽略檔案設定
├── .flake8                            # Flake8 程式碼檢查設定
├── logger_config.py                   # Logging 配置模組
├── call_login_api.py                  # API 登入功能
├── import_user.py                     # 員工資料匯入功能
├── query_user_table_sqlalchemy.py    # 資料庫查詢功能 (SQLAlchemy)
├── main.py                            # 主程式（整合匯入和測試功能）
├── SHA_256.py                         # SHA256 密碼雜湊工具
├── network_speedtest.py               # 網路速度測試工具
├── 默认模块.openapi.json              # OpenAPI 規範文件
├── .github/
│   └── workflows/
│       └── python-package-conda.yml   # GitHub Actions CI/CD 設定
└── logs/                              # 日誌檔案目錄（自動產生）
    ├── main_YYYYMMDD.log
    ├── import_user_YYYYMMDD.log
    ├── call_login_api_YYYYMMDD.log
    └── query_user_table_sqlalchemy_YYYYMMDD.log
```

## 依賴套件

- `requests` - HTTP 請求庫
- `urllib3` - HTTP 客戶端庫（用於重試機制）
- `pyodbc` - SQL Server 資料庫連接（ODBC 驅動）
- `sqlalchemy` - SQL 工具包和 ORM
- `pandas` - 資料處理和分析
- `openpyxl` - Excel 檔案讀寫
- `python-dotenv` - 環境變數管理
- `tqdm` - 進度條顯示
- `speedtest-cli` - 網路速度測試（用於 network_speedtest.py）
- `schedule` - 任務排程（用於 network_speedtest.py）

## 注意事項

1. **安全性**

   - `.env` 檔案包含敏感資訊，請確保不要提交到版本控制系統
   - 建議使用 `.gitignore` 排除 `.env` 檔案

2. **ODBC Driver**

   - 確保已安裝正確版本的 ODBC Driver
   - 如果遇到連接問題，請檢查 ODBC Driver 是否正確安裝

3. **資料庫權限**

   - 確保資料庫使用者有足夠的權限查詢目標表
   - 建議使用最小權限原則

4. **API 認證**
   - 妥善保管 API 憑證資訊
   - 定期更新密碼和 token

## Logging 使用

所有腳本都使用統一的 logging 系統，取代了原本的 `print` 語句。日誌會同時輸出到：

1. **控制台** - 即時查看執行狀況
2. **日誌檔案** - 永久記錄，方便後續追蹤

**日誌級別說明：**

- `logger.debug()` - 詳細除錯資訊（僅在 DEBUG 級別顯示）
- `logger.info()` - 一般資訊訊息
- `logger.warning()` - 警告訊息
- `logger.error()` - 錯誤訊息（包含堆疊追蹤）

**範例：**

```python
from logger_config import setup_logger

logger = setup_logger("my_module")
logger.info("這是一般資訊")
logger.error("這是錯誤訊息", exc_info=True)  # exc_info=True 會包含堆疊追蹤
```

## 疑難排解

### 資料庫連接失敗

**錯誤訊息：** `[Microsoft][ODBC Driver Manager] Data source name not found`

**解決方法：**

1. 確認已安裝 ODBC Driver 17 for SQL Server
2. 檢查連接字串中的伺服器位址和資料庫名稱是否正確
3. 確認網路連線正常

### API 請求失敗

**錯誤訊息：** `401 Unauthorized`

**解決方法：**

1. 檢查 `.env` 檔案中的 API 設定是否正確
2. 確認 client_id、client_secret、username、password 是否正確
3. 檢查 API 基礎 URL 是否可訪問
4. 如果使用 Bearer Token，確認 `API_ACCESS_TOKEN` 是否正確設定

### 員工匯入失敗

**錯誤訊息：** `400 Bad Request` 或 `404 Not Found`

**解決方法：**

1. 確認 API 路徑是否正確（`/membership/api/app/users/import-from-hireme`）
2. 檢查請求格式是否為 JSON：`{"LoginName": "xxx"}`
3. 確認 `LoginName` 欄位名稱大小寫正確
4. 檢查 API 服務是否正常運行

### 編碼問題

如果遇到中文顯示問題，請確保：

1. `.env` 檔案使用 UTF-8 編碼
2. CSV 檔案使用 `utf-8-sig` 編碼（已在程式碼中設定）

## 授權

本專案僅供內部使用。

## 聯絡資訊

如有問題或建議，請聯絡專案維護者。
