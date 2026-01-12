# 設定 Windows 使用 PowerShell
# 使用WSL 或是 linux 幫我註解這邊
set shell := ["powershell.exe", "-c"]


# 預設任務:顯示所有可用的指令
default:
    @just --list
