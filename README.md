# JBHRIS Import 專案

這是一個用於連接 JBHRIS 系統的 Python 工具集，包含 API 登入功能和資料庫查詢功能。

## 功能說明

### 1. API 登入功能 (`call_login_api.py`)

- 使用 OAuth2/OIDC password grant type 進行登入
- 支援取得 access token 和 refresh token
- 支援使用 refresh token 刷新 access token
- 支援多租戶設定

### 2. 資料庫查詢功能 (`query_user_table_sqlalchemy.py`)
- 使用 SQLAlchemy 連接 SQL Server 資料庫
- 查詢 user 表的資料
- 顯示表結構資訊
- 支援連接池管理，提高效能
- 支援自訂 SQL 查詢
- 與 pandas 完美整合

### 4. Logging 功能 (`logger_config.py`)

- 統一的日誌記錄系統
- 支援控制台和檔案輸出
- 自動輪轉日誌檔案（防止檔案過大）
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
API_BASE_URL=http://192.168.1.109:5050
API_CLIENT_ID=your_client_id
API_CLIENT_SECRET=your_client_secret
API_USERNAME=your_username
API_PASSWORD=your_password
API_TENANT=

# Logging 設定（可選）
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**重要：** `.env` 檔案包含敏感資訊，請勿將其提交到版本控制系統。

### 3. Logging 設定

日誌檔案會自動儲存在 `logs/` 目錄下：

- `logs/query_user_table.log` - 資料庫查詢相關日誌
- `logs/call_login_api.log` - API 呼叫相關日誌

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

或執行主程式：

```bash
python main.py
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

```
.
├── README.md                          # 專案說明文件
├── requirements.txt                   # Python 依賴套件清單
├── .env                               # 環境變數設定（不提交到版本控制）
├── .env.example                       # 環境變數範本
├── .gitignore                         # Git 忽略檔案設定
├── logger_config.py                   # Logging 配置模組
├── call_login_api.py                  # API 登入功能
├── query_user_table_sqlalchemy.py    # 資料庫查詢功能 (SQLAlchemy)
├── main.py                            # 主程式
├── 默认模块.openapi.json              # OpenAPI 規範文件
└── logs/                              # 日誌檔案目錄（自動產生）
    ├── query_user_table.log
    ├── query_user_table_sqlalchemy.log
    └── call_login_api.log
```

## 依賴套件

- `requests` - HTTP 請求庫
- `pyodbc` - SQL Server 資料庫連接（ODBC 驅動）
- `sqlalchemy` - SQL 工具包和 ORM（可選，用於 SQLAlchemy 版本）
- `pandas` - 資料處理和分析
- `openpyxl` - Excel 檔案讀寫
- `python-dotenv` - 環境變數管理

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

### 編碼問題

如果遇到中文顯示問題，請確保：

1. `.env` 檔案使用 UTF-8 編碼
2. CSV 檔案使用 `utf-8-sig` 編碼（已在程式碼中設定）

## 授權

本專案僅供內部使用。

## 聯絡資訊

如有問題或建議，請聯絡專案維護者。
