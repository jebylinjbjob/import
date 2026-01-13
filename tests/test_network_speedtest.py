"""
network_speedtest 模組單元測試
測試網速測試和資料儲存功能
"""

import os
import csv
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, call
from network_speedtest import (
    test_speed as network_test_speed,
    save_to_csv,
    run_speedtest,
    CSV_FILE
)


class TestTestSpeed:
    """測試 test_speed 函式"""

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_success(self, mock_speedtest_class):
        """測試成功執行網速測試"""
        # 建立 mock speedtest 物件
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st

        # 設定 mock 伺服器資訊
        mock_st.results.server = {
            'name': 'Test Server',
            'country': 'Taiwan',
            'sponsor': 'Test ISP'
        }
        mock_st.results.ping = 15.5

        # 設定 mock 速度（單位為 bps，需轉換為 Mbps）
        mock_st.download.return_value = 100_000_000  # 100 Mbps
        mock_st.upload.return_value = 50_000_000    # 50 Mbps

        result = network_test_speed()

        # 驗證結果
        assert result is not None
        assert 'timestamp' in result
        assert result['download_mbps'] == 100.0
        assert result['upload_mbps'] == 50.0
        assert result['ping_ms'] == 15.5
        assert result['server_name'] == 'Test Server'
        assert result['server_country'] == 'Taiwan'
        assert result['server_sponsor'] == 'Test ISP'

        # 驗證方法被呼叫
        mock_st.get_best_server.assert_called_once()
        mock_st.download.assert_called_once()
        mock_st.upload.assert_called_once()

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_without_sponsor(self, mock_speedtest_class):
        """測試伺服器資訊沒有 sponsor 欄位"""
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st

        mock_st.results.server = {
            'name': 'Test Server',
            'country': 'Taiwan'
            # 沒有 sponsor 欄位
        }
        mock_st.results.ping = 20.0
        mock_st.download.return_value = 80_000_000
        mock_st.upload.return_value = 40_000_000

        result = network_test_speed()

        assert result is not None
        assert result['server_sponsor'] == 'N/A'

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_decimal_values(self, mock_speedtest_class):
        """測試小數值處理和四捨五入"""
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st

        mock_st.results.server = {
            'name': 'Test Server',
            'country': 'Taiwan',
            'sponsor': 'ISP'
        }
        mock_st.results.ping = 12.3456789
        mock_st.download.return_value = 123_456_789  # 123.456789 Mbps
        mock_st.upload.return_value = 45_678_901     # 45.678901 Mbps

        result = network_test_speed()

        assert result is not None
        assert result['download_mbps'] == 123.46  # 四捨五入到小數點後 2 位
        assert result['upload_mbps'] == 45.68
        assert result['ping_ms'] == 12.35

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_exception_handling(self, mock_speedtest_class):
        """測試例外處理"""
        mock_speedtest_class.side_effect = Exception("Network error")

        result = network_test_speed()

        assert result is None

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_get_best_server_fails(self, mock_speedtest_class):
        """測試選擇伺服器失敗"""
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st
        mock_st.get_best_server.side_effect = Exception("No server available")

        result = network_test_speed()

        assert result is None

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_download_fails(self, mock_speedtest_class):
        """測試下載測試失敗"""
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st
        mock_st.results.server = {'name': 'Test', 'country': 'TW', 'sponsor': 'ISP'}
        mock_st.download.side_effect = Exception("Download failed")

        result = network_test_speed()

        assert result is None

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_upload_fails(self, mock_speedtest_class):
        """測試上傳測試失敗"""
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st
        mock_st.results.server = {'name': 'Test', 'country': 'TW', 'sponsor': 'ISP'}
        mock_st.download.return_value = 100_000_000
        mock_st.upload.side_effect = Exception("Upload failed")

        result = network_test_speed()

        assert result is None

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_timestamp_format(self, mock_speedtest_class):
        """測試時間戳記格式"""
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st
        mock_st.results.server = {'name': 'Test', 'country': 'TW', 'sponsor': 'ISP'}
        mock_st.results.ping = 10.0
        mock_st.download.return_value = 100_000_000
        mock_st.upload.return_value = 50_000_000

        result = network_test_speed()

        assert result is not None
        # 驗證時間戳記格式為 YYYY-MM-DD HH:MM:SS
        timestamp = result['timestamp']
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_zero_values(self, mock_speedtest_class):
        """測試速度為 0 的情況"""
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st
        mock_st.results.server = {'name': 'Test', 'country': 'TW', 'sponsor': 'ISP'}
        mock_st.results.ping = 0.0
        mock_st.download.return_value = 0
        mock_st.upload.return_value = 0

        result = network_test_speed()

        assert result is not None
        assert result['download_mbps'] == 0.0
        assert result['upload_mbps'] == 0.0
        assert result['ping_ms'] == 0.0

    @patch('network_speedtest.speedtest.Speedtest')
    def test_speed_very_high_values(self, mock_speedtest_class):
        """測試極高速度值"""
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st
        mock_st.results.server = {'name': 'Test', 'country': 'TW', 'sponsor': 'ISP'}
        mock_st.results.ping = 1.5
        mock_st.download.return_value = 1_000_000_000  # 1000 Mbps (1 Gbps)
        mock_st.upload.return_value = 500_000_000      # 500 Mbps

        result = network_test_speed()

        assert result is not None
        assert result['download_mbps'] == 1000.0
        assert result['upload_mbps'] == 500.0


class TestSaveToCsv:
    """測試 save_to_csv 函式"""

    def test_save_to_csv_new_file(self, tmp_path):
        """測試儲存到新檔案（含標題列）"""
        csv_file = tmp_path / "test_speedtest.csv"

        result = {
            'timestamp': '2026-01-13 10:30:00',
            'download_mbps': 100.5,
            'upload_mbps': 50.25,
            'ping_ms': 15.75,
            'server_name': 'Test Server',
            'server_country': 'Taiwan',
            'server_sponsor': 'Test ISP'
        }

        with patch('network_speedtest.CSV_FILE', str(csv_file)):
            save_to_csv(result)

        # 驗證檔案存在
        assert csv_file.exists()

        # 驗證內容
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert len(rows) == 1
            assert rows[0]['timestamp'] == '2026-01-13 10:30:00'
            assert rows[0]['download_mbps'] == '100.5'
            assert rows[0]['upload_mbps'] == '50.25'
            assert rows[0]['ping_ms'] == '15.75'
            assert rows[0]['server_name'] == 'Test Server'

    def test_save_to_csv_append_to_existing(self, tmp_path):
        """測試附加到現有檔案（不重複標題列）"""
        csv_file = tmp_path / "test_speedtest.csv"

        # 建立現有檔案
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'download_mbps', 'upload_mbps', 'ping_ms',
                'server_name', 'server_country', 'server_sponsor'
            ])
            writer.writeheader()
            writer.writerow({
                'timestamp': '2026-01-13 09:00:00',
                'download_mbps': 90.0,
                'upload_mbps': 45.0,
                'ping_ms': 20.0,
                'server_name': 'Old Server',
                'server_country': 'Taiwan',
                'server_sponsor': 'Old ISP'
            })

        # 新增第二筆資料
        result = {
            'timestamp': '2026-01-13 10:00:00',
            'download_mbps': 100.0,
            'upload_mbps': 50.0,
            'ping_ms': 15.0,
            'server_name': 'New Server',
            'server_country': 'Taiwan',
            'server_sponsor': 'New ISP'
        }

        with patch('network_speedtest.CSV_FILE', str(csv_file)):
            save_to_csv(result)

        # 驗證內容
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert len(rows) == 2
            assert rows[0]['server_name'] == 'Old Server'
            assert rows[1]['server_name'] == 'New Server'

    def test_save_to_csv_multiple_entries(self, tmp_path):
        """測試儲存多筆資料"""
        csv_file = tmp_path / "test_speedtest.csv"

        results = [
            {
                'timestamp': f'2026-01-13 {i:02d}:00:00',
                'download_mbps': 100.0 + i,
                'upload_mbps': 50.0 + i,
                'ping_ms': 15.0 + i,
                'server_name': f'Server {i}',
                'server_country': 'Taiwan',
                'server_sponsor': f'ISP {i}'
            }
            for i in range(5)
        ]

        with patch('network_speedtest.CSV_FILE', str(csv_file)):
            for result in results:
                save_to_csv(result)

        # 驗證內容
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert len(rows) == 5
            for i, row in enumerate(rows):
                assert row['server_name'] == f'Server {i}'
                assert float(row['download_mbps']) == 100.0 + i

    def test_save_to_csv_utf8_encoding(self, tmp_path):
        """測試 UTF-8 編碼處理中文字元"""
        csv_file = tmp_path / "test_speedtest_utf8.csv"

        result = {
            'timestamp': '2026-01-13 10:30:00',
            'download_mbps': 100.0,
            'upload_mbps': 50.0,
            'ping_ms': 15.0,
            'server_name': '台灣伺服器',
            'server_country': '台灣',
            'server_sponsor': '中華電信'
        }

        with patch('network_speedtest.CSV_FILE', str(csv_file)):
            save_to_csv(result)

        # 驗證可以正確讀取中文
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert rows[0]['server_name'] == '台灣伺服器'
            assert rows[0]['server_country'] == '台灣'
            assert rows[0]['server_sponsor'] == '中華電信'

    @patch('network_speedtest.open')
    @patch('network_speedtest.logger')
    def test_save_to_csv_exception(self, mock_logger, mock_open):
        """測試儲存時發生例外"""
        mock_open.side_effect = IOError("Permission denied")

        result = {
            'timestamp': '2026-01-13 10:30:00',
            'download_mbps': 100.0,
            'upload_mbps': 50.0,
            'ping_ms': 15.0,
            'server_name': 'Test Server',
            'server_country': 'Taiwan',
            'server_sponsor': 'ISP'
        }

        save_to_csv(result)

        # 驗證錯誤被記錄
        assert mock_logger.error.called

    def test_save_to_csv_fieldnames_order(self, tmp_path):
        """測試欄位順序正確"""
        csv_file = tmp_path / "test_speedtest_order.csv"

        result = {
            'timestamp': '2026-01-13 10:30:00',
            'download_mbps': 100.0,
            'upload_mbps': 50.0,
            'ping_ms': 15.0,
            'server_name': 'Test Server',
            'server_country': 'Taiwan',
            'server_sponsor': 'ISP'
        }

        with patch('network_speedtest.CSV_FILE', str(csv_file)):
            save_to_csv(result)

        # 驗證欄位順序
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)

            expected_order = [
                'timestamp', 'download_mbps', 'upload_mbps', 'ping_ms',
                'server_name', 'server_country', 'server_sponsor'
            ]
            assert header == expected_order


class TestRunSpeedtest:
    """測試 run_speedtest 函式"""

    @patch('network_speedtest.save_to_csv')
    @patch('network_speedtest.test_speed')
    def test_run_speedtest_success(self, mock_network_test_speed, mock_save_to_csv):
        """測試成功執行速度測試並儲存"""
        mock_result = {
            'timestamp': '2026-01-13 10:30:00',
            'download_mbps': 100.0,
            'upload_mbps': 50.0,
            'ping_ms': 15.0,
            'server_name': 'Test Server',
            'server_country': 'Taiwan',
            'server_sponsor': 'ISP'
        }
        mock_network_test_speed.return_value = mock_result

        run_speedtest()

        mock_network_test_speed.assert_called_once()
        mock_save_to_csv.assert_called_once_with(mock_result)

    @patch('network_speedtest.save_to_csv')
    @patch('network_speedtest.test_speed')
    @patch('network_speedtest.logger')
    def test_run_speedtest_failure(self, mock_logger, mock_network_test_speed, mock_save_to_csv):
        """測試速度測試失敗時不儲存結果"""
        mock_network_test_speed.return_value = None

        run_speedtest()

        mock_network_test_speed.assert_called_once()
        mock_save_to_csv.assert_not_called()
        mock_logger.warning.assert_called_once()


class TestIntegration:
    """整合測試"""

    @patch('network_speedtest.speedtest.Speedtest')
    def test_complete_workflow(self, mock_speedtest_class, tmp_path):
        """測試完整工作流程：測試速度 -> 儲存 CSV"""
        csv_file = tmp_path / "integration_test.csv"

        # 設定 mock speedtest
        mock_st = Mock()
        mock_speedtest_class.return_value = mock_st
        mock_st.results.server = {
            'name': 'Integration Test Server',
            'country': 'Taiwan',
            'sponsor': 'Test ISP'
        }
        mock_st.results.ping = 12.34
        mock_st.download.return_value = 123_456_789
        mock_st.upload.return_value = 45_678_901

        # 執行測試
        result = network_test_speed()

        # 驗證測試結果
        assert result is not None
        assert result['download_mbps'] == 123.46
        assert result['upload_mbps'] == 45.68
        assert result['ping_ms'] == 12.34

        # 儲存到 CSV
        with patch('network_speedtest.CSV_FILE', str(csv_file)):
            save_to_csv(result)

        # 驗證檔案內容
        assert csv_file.exists()
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert len(rows) == 1
            assert rows[0]['server_name'] == 'Integration Test Server'
            assert rows[0]['download_mbps'] == '123.46'
            assert rows[0]['upload_mbps'] == '45.68'
            assert rows[0]['ping_ms'] == '12.34'

    def test_result_dictionary_structure(self):
        """測試結果字典結構完整性"""
        required_keys = [
            'timestamp',
            'download_mbps',
            'upload_mbps',
            'ping_ms',
            'server_name',
            'server_country',
            'server_sponsor'
        ]

        # 模擬一個結果字典
        result = {
            'timestamp': '2026-01-13 10:30:00',
            'download_mbps': 100.0,
            'upload_mbps': 50.0,
            'ping_ms': 15.0,
            'server_name': 'Test Server',
            'server_country': 'Taiwan',
            'server_sponsor': 'ISP'
        }

        # 驗證所有必要的鍵都存在
        for key in required_keys:
            assert key in result
