"""
Logging 配置模組
"""

import os
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()


def setup_logger(
    name: str,
    log_file: str = None,
    log_level: str = None,
    console_output: bool = True,
    file_output: bool = True
) -> logging.Logger:
    """
    設定並返回 logger 實例

    Args:
        name: logger 名稱
        log_file: 日誌檔案路徑（可選，預設為 logs/{name}.log）
        log_level: 日誌級別（可選，從環境變數 LOG_LEVEL 讀取，預設為 INFO）
        console_output: 是否輸出到控制台
        file_output: 是否輸出到檔案

    Returns:
        配置好的 logger 實例
    """
    # 獲取日誌級別
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    level = getattr(logging, log_level, logging.INFO)

    # 創建 logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重複添加 handler
    if logger.handlers:
        return logger

    # 設定日誌格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台輸出
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 檔案輸出
    if file_output:
        if log_file is None:
            # 確保 logs 目錄存在
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            # 在檔案名稱中加入日期
            date_str = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(log_dir, f"{name}_{date_str}.log")

        # 使用 RotatingFileHandler 限制檔案大小
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

