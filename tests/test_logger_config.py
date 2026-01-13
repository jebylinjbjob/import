"""
logger_config 模組單元測試
"""

import pytest
import logging
from pathlib import Path
from logger_config import setup_logger


class TestSetupLogger:
    """測試 setup_logger 函式"""

    def test_setup_logger_returns_logger(self, tmp_path):
        """測試建立 logger 並返回正確型別"""
        log_file = str(tmp_path / "test1.log")
        logger = setup_logger("test_logger_1", log_file=log_file)
        assert isinstance(logger, logging.Logger)

    def test_logger_name(self, tmp_path):
        """測試 logger 名稱正確設定"""
        logger_name = "my_test_logger_2"
        log_file = str(tmp_path / "test2.log")
        logger = setup_logger(logger_name, log_file=log_file)
        assert logger.name == logger_name

    def test_default_log_level(self, tmp_path):
        """測試預設日誌級別為 INFO"""
        log_file = str(tmp_path / "test3.log")
        logger = setup_logger("test_logger_3", log_file=log_file)
        assert logger.level == logging.INFO

    def test_custom_log_level_debug(self, tmp_path):
        """測試自訂日誌級別為 DEBUG"""
        log_file = str(tmp_path / "test4.log")
        logger = setup_logger("test_logger_4", log_level="DEBUG", log_file=log_file)
        assert logger.level == logging.DEBUG

    def test_console_handler_enabled(self, tmp_path):
        """測試控制台 handler 已啟用"""
        log_file = str(tmp_path / "test5.log")
        logger = setup_logger("test_logger_5", console_output=True, file_output=False, log_file=log_file)
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not hasattr(h, 'baseFilename')]
        assert len(console_handlers) > 0

    def test_file_handler_enabled(self, tmp_path):
        """測試檔案 handler 已啟用"""
        log_file = str(tmp_path / "test6.log")
        logger = setup_logger("test_logger_6", console_output=False, file_output=True, log_file=log_file)
        file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
        assert len(file_handlers) > 0

    def test_both_handlers_enabled(self, tmp_path):
        """測試同時啟用控制台和檔案 handler"""
        log_file = str(tmp_path / "test7.log")
        logger = setup_logger("test_logger_7", console_output=True, file_output=True, log_file=log_file)
        assert len(logger.handlers) >= 2

    def test_no_handlers(self, tmp_path):
        """測試停用所有 handler"""
        log_file = str(tmp_path / "test8.log")
        logger = setup_logger("test_logger_8", console_output=False, file_output=False, log_file=log_file)
        assert len(logger.handlers) == 0

    def test_log_file_created(self, tmp_path):
        """測試日誌檔案已建立"""
        log_file = str(tmp_path / "test9.log")
        logger = setup_logger("test_logger_9", console_output=False, file_output=True, log_file=log_file)
        logger.info("Test message")

        # 強制關閉 handler
        for handler in logger.handlers:
            handler.close()

        assert Path(log_file).exists()


# 如果直接執行此檔案，顯示測試資訊
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
