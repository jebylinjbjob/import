# JBHRIS Import 專案

本專案提供多個資料分析與統計工具，用於處理 JBHRIS 系統的相關資料。

## 快速開始

### 使用 justfile（推薦）

本專案使用 [just](https://github.com/casey/just) 作為任務執行器，讓您可以用簡單的指令管理專案。

####  安裝 just（如果尚未安裝）

```bash
winget install --id Casey.Just --exact
```

#### 初始化專案

```bash
just init
```

這個指令會自動：

- 檢查並建立虛擬環境（.venv 或 venv）
- 建立 .env 檔案（從 .env.example 複製）
- 安裝所有依賴套件


#### 設定環境變數

複製 `.env.example` 為 `.env` 並填入實際的資料庫連接資訊：

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

然後編輯 `.env` 檔案，填入您的資料庫連接資訊：

```env
DB_SERVER=your_database_server
DB_DATABASE=JbJobMembership
DB_DATABASE_HireMePlz=HireMePlz
DB_DATABASE_JBHRIS_DISPATCH=JBHRIS_DISPATCH
DB_USER_ID=your_username
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 17 for SQL Server

LOG_LEVEL=INFO
```
