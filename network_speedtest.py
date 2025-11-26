"""
網速測試工具
每小時自動測試一次網速並記錄結果
"""

import os
import time
import csv
import schedule
from datetime import datetime
from typing import Dict, Optional
import speedtest
from logger_config import setup_logger
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 設定 logger
logger = setup_logger("speedtest")

# CSV 檔案路徑
CSV_FILE = "speedtest_results.csv"


def test_speed() -> Optional[Dict[str, float]]:
    """
    執行網速測試

    Returns:
        包含下載速度、上傳速度和延遲的字典，如果失敗則返回 None
    """
    try:
        logger.info("開始測試網速...")

        # 創建 Speedtest 物件
        st = speedtest.Speedtest()

        # 選擇最佳伺服器
        logger.info("正在選擇最佳伺服器...")
        st.get_best_server()
        server_info = st.results.server
        logger.info(f"使用伺服器: {server_info['name']} ({server_info['country']})")

        # 測試下載速度
        logger.info("正在測試下載速度...")
        download_speed = st.download() / 1_000_000  # 轉換為 Mbps

        # 測試上傳速度
        logger.info("正在測試上傳速度...")
        upload_speed = st.upload() / 1_000_000  # 轉換為 Mbps

        # 獲取延遲（ping）
        ping = st.results.ping

        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "download_mbps": round(download_speed, 2),
            "upload_mbps": round(upload_speed, 2),
            "ping_ms": round(ping, 2),
            "server_name": server_info['name'],
            "server_country": server_info['country'],
            "server_sponsor": server_info.get('sponsor', 'N/A')
        }

        logger.info(f"測試完成 - 下載: {result['download_mbps']} Mbps, "
                   f"上傳: {result['upload_mbps']} Mbps, "
                   f"延遲: {result['ping_ms']} ms")

        return result

    except Exception as e:
        logger.error(f"網速測試失敗: {e}", exc_info=True)
        return None


def save_to_csv(result: Dict[str, float]) -> None:
    """
    將測試結果儲存到 CSV 檔案

    Args:
        result: 測試結果字典
    """
    file_exists = os.path.isfile(CSV_FILE)

    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
            fieldnames = [
                'timestamp',
                'download_mbps',
                'upload_mbps',
                'ping_ms',
                'server_name',
                'server_country',
                'server_sponsor'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # 如果檔案不存在，寫入標題行
            if not file_exists:
                writer.writeheader()

            writer.writerow(result)

        logger.debug(f"結果已儲存到 {CSV_FILE}")

    except Exception as e:
        logger.error(f"儲存結果到 CSV 失敗: {e}")


def run_speedtest():
    """
    執行網速測試並儲存結果
    """
    result = test_speed()

    if result:
        save_to_csv(result)

        # 輸出到控制台
        print(f"\n{'='*60}")
        print(f"網速測試結果 - {result['timestamp']}")
        print(f"{'='*60}")
        print(f"下載速度: {result['download_mbps']} Mbps")
        print(f"上傳速度: {result['upload_mbps']} Mbps")
        print(f"延遲 (Ping): {result['ping_ms']} ms")
        print(f"伺服器: {result['server_name']} ({result['server_country']})")
        print(f"{'='*60}\n")
    else:
        logger.warning("網速測試失敗，結果未儲存")


def main():
    """
    主函數 - 設定定時任務並執行
    """
    # 立即執行一次測試
    logger.info("啟動網速測試工具")
    print("網速測試工具已啟動")
    print("將每小時自動測試一次網速")
    print(f"結果會儲存到: {CSV_FILE}")
    print("按 Ctrl+C 停止程式\n")

    run_speedtest()

    # 設定每小時執行一次
    schedule.every().hour.do(run_speedtest)

    # 顯示下次執行時間
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"下次測試時間: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"下次測試時間: {next_run.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 持續執行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次是否有待執行的任務

    except KeyboardInterrupt:
        logger.info("程式已停止")
        print("\n程式已停止")


if __name__ == "__main__":
    main()

