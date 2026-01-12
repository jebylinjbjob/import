# JBHRIS Import 專案

本專案提供多個資料分析與統計工具，用於處理 JBHRIS 系統的相關資料。

## 快速開始

### 使用 justfile（推薦）

本專案使用 [just](https://github.com/casey/just) 作為任務執行器，讓您可以用簡單的指令管理專案。

#### 1. 安裝 just（如果尚未安裝）

```bash
# Windows (使用 cargo)
cargo install just

# 或使用預編譯版本
# 下載：https://github.com/casey/just/releases
```

#### 2. 初始化專案

```bash
just init
```

這個指令會自動：

- 檢查並建立虛擬環境（.venv 或 venv）
- 建立 .env 檔案（從 .env.example 複製）
- 安裝所有依賴套件

#### 3. 執行任務

```bash
# 查看所有可用任務
just

# 執行 HireMe 註冊人數統計
just hireme

# 執行前台登入次數統計
just login

# 執行所有報告
just all

# 執行網速測試
just speedtest

# 檢查環境變數設定
just check-env

# 更新依賴套件
just update

# 清理虛擬環境
just clean
```

## 環境設置

### 方法一：使用 uv（推薦，速度更快）

[uv](https://github.com/astral-sh/uv) 是一個極速的 Python 套件與專案管理工具，執行速度比傳統的 pip、virtualenv 快上 10-100 倍。

#### 1. 安裝 uv

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 建立虛擬環境並安裝依賴

```bash
# 使用 uv 建立虛擬環境（會在 .venv 目錄）
uv venv

# 啟動虛擬環境
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 從 requirements.txt 安裝依賴（速度比 pip 快很多）
uv pip install -r requirements.txt
```

或者使用 uv 的現代工作流程（不需要手動啟動虛擬環境）：

```bash
# 直接使用 uv 執行，會自動管理虛擬環境和依賴
uv run python hireme.py
uv run python membership_DB_for_login.py
uv run python network_speedtest.py
```

#### 3. 設定環境變數

複製 `.env.example` 為 `.env` 並填入實際的資料庫連接資訊：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

然後編輯 `.env` 檔案，填入您的資料庫連接資訊：

```env
# 資料庫連接設定
DB_SERVER=your_database_server
DB_DATABASE=your_database_name
DB_USER_ID=your_username
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 17 for SQL Server

# 日誌設定（可選）
LOG_LEVEL=INFO
```

**uv 的優勢：**

- ⚡ 執行速度比 pip 快 10-100 倍
- 🔒 自動管理虛擬環境，無需手動啟動
- 📦 自動同步依賴，確保環境一致
- 🚀 支援現代 Python 專案工作流程

### 方法二：使用傳統 venv

#### 1. 建立虛擬環境（venv）

```bash
# 在專案根目錄執行
python -m venv venv

# Windows 啟動虛擬環境
venv\Scripts\activate

# Linux/Mac 啟動虛擬環境
source venv/bin/activate
```

#### 2. 安裝依賴套件

```bash
pip install -r requirements.txt
```

#### 3. 設定環境變數

複製 `.env.example` 為 `.env` 並填入實際的資料庫連接資訊：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

然後編輯 `.env` 檔案，填入您的資料庫連接資訊（同上）。

#### 4. 執行程式

```bash
# 執行 HireMe 註冊人數統計
python hireme.py

# 執行前台登入次數統計
python membership_DB_for_login.py

# 執行網速測試
python network_speedtest.py
```

## 專案結構

```
.
├── hireme.py                      # HireMe 註冊人數統計報告
├── membership_DB_for_login.py     # 前台登入次數統計
├── network_speedtest.py            # 網速測試工具
├── SHA_256.py                      # 密碼雜湊工具
├── logger_config.py                # 日誌配置模組
├── justfile                        # just 任務定義檔
├── requirements.txt                # 依賴套件清單
├── .env.example                    # 環境變數範本
├── .env                            # 環境變數檔案（需自行建立）
└── README.md                       # 本檔案
```

## 主要功能

### 1. HireMe 註冊人數統計 (`hireme.py`)

產生週報格式的註冊人數統計報告，包含：

- 總註冊人數（指定日期區間）
- 每週註冊人數統計
- 輸出為 CSV 格式

**統計區間：**

- 2025/11 月（第 3 週 11/17~11/23）
- 2025/11 月（第 4 週 11/24~11/30）
- 2025/12 月（第 1 週 12/1~12/7）
- 2025/12 月（第 2 週 12/8~12/14）
- 2025/12 月（第 3 週 12/15~12/21）
- 2025/12 月（第 4 週 12/22~12/28）
- 2026/01 月（第 1 週 12/29~1/4）
- 2026/01 月（第 2 週 1/5~1/11）

**執行方式：**

```bash
just hireme
# 或
uv run python hireme.py
# 或
python hireme.py
```

### 2. 前台登入次數統計 (`membership_DB_for_login.py`)

統計前台系統的登入次數，包含：

- 總登入次數（指定日期區間）
- 每週登入次數統計
- 輸出為 CSV 格式

**統計區間：** 與 HireMe 註冊統計相同

**執行方式：**

```bash
just login
# 或
uv run python membership_DB_for_login.py
# 或
python membership_DB_for_login.py
```

### 3. 網速測試 (`network_speedtest.py`)

測試網路連線速度。

**執行方式：**

```bash
just speedtest
# 或
uv run python network_speedtest.py
# 或
python network_speedtest.py
```

## 環境變數管理

### 使用 .env 檔案

專案使用 `python-dotenv` 來管理環境變數，所有敏感資訊（如資料庫密碼）都應該存放在 `.env` 檔案中。

**環境變數說明：**

| 變數名稱      | 說明             | 範例                                |
| ------------- | ---------------- | ----------------------------------- |
| `DB_SERVER`   | 資料庫伺服器位址 | `dwinsdb.local`                     |
| `DB_DATABASE` | 資料庫名稱       | `JbJobMembership`                   |
| `DB_USER_ID`  | 資料庫使用者名稱 | `your_username`                     |
| `DB_PASSWORD` | 資料庫密碼       | `your_password`                     |
| `DB_DRIVER`   | ODBC 驅動程式    | `ODBC Driver 17 for SQL Server`     |
| `LOG_LEVEL`   | 日誌級別（可選） | `INFO`, `DEBUG`, `WARNING`, `ERROR` |

### 檢查環境變數

使用 justfile 快速檢查環境變數設定：

```bash
just check-env
```

## justfile 任務說明

| 任務                     | 說明                                                  |
| ------------------------ | ----------------------------------------------------- |
| `just` 或 `just default` | 顯示所有可用的指令                                    |
| `just init`              | 檢查並初始化專案（建立虛擬環境、.env 檔案、安裝依賴） |
| `just hireme`            | 執行 HireMe 註冊人數統計                              |
| `just login`             | 執行前台登入次數統計                                  |
| `just speedtest`         | 執行網速測試                                          |
| `just all`               | 執行所有報告（hireme + login）                        |
| `just update`            | 更新依賴套件                                          |
| `just clean`             | 清理虛擬環境                                          |
| `just check-env`         | 檢查環境變數設定                                      |

## 依賴套件

- `pyodbc>=5.0.0` - SQL Server 資料庫連接
- `python-dotenv>=1.0.0` - 環境變數管理
- `sqlalchemy>=2.0.0` - ORM 資料庫操作
- `speedtest-cli>=2.1.3` - 網速測試
- `schedule>=1.2.0` - 任務排程

## 注意事項

- `.env` 檔案已加入 `.gitignore`，不會被提交到版本控制
- `.env.example` 是範本檔案，可以提交到版本控制
- 請妥善保管 `.env` 檔案中的敏感資訊（密碼等）
- 虛擬環境目錄 `.venv/` 和 `venv/` 都已加入 `.gitignore`
- 使用 `uv` 時，建議使用 `.venv` 作為虛擬環境目錄名稱（uv 的預設值）
- `justfile` 會自動偵測 `uv` 是否已安裝，如果已安裝則優先使用 `uv`，否則使用傳統 `pip`
- 在 Windows 上，`justfile` 使用 PowerShell 語法；在 Linux/Mac 上，請註解掉 PowerShell 設定並使用 bash 語法

## 參考資源

- [just 官方文件](https://github.com/casey/just)
- [uv 官方文件](https://github.com/astral-sh/uv)
- [SQLAlchemy 文件](https://docs.sqlalchemy.org/)
