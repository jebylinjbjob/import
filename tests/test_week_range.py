"""
週範圍模組單元測試
"""

import pytest
from datetime import date
from week_range import get_week_ranges, get_total_date_range


class TestWeekRanges:
    """測試週範圍功能"""

    def test_get_week_ranges_returns_list(self):
        """測試 get_week_ranges 回傳列表"""
        weeks = get_week_ranges()
        assert isinstance(weeks, list)
        assert len(weeks) > 0

    def test_get_week_ranges_structure(self):
        """測試週範圍的資料結構"""
        weeks = get_week_ranges()
        for week in weeks:
            assert isinstance(week, tuple)
            assert len(week) == 4
            assert isinstance(week[0], str)  # 描述
            assert isinstance(week[1], date)  # 開始日期
            assert isinstance(week[2], date)  # 結束日期
            assert isinstance(week[3], str)  # 週標籤

    def test_get_week_ranges_date_order(self):
        """測試週範圍的日期順序正確"""
        weeks = get_week_ranges()
        for week in weeks:
            start_date = week[1]
            end_date = week[2]
            assert start_date <= end_date, f"開始日期應小於等於結束日期: {week[0]}"

    def test_get_week_ranges_continuous(self):
        """測試週範圍是否連續"""
        weeks = get_week_ranges()
        for i in range(len(weeks) - 1):
            current_end = weeks[i][2]
            next_start = weeks[i + 1][1]
            # 檢查下一週開始日期是否緊接著當前週結束日期
            diff = (next_start - current_end).days
            assert diff == 1, f"週之間應該連續: {weeks[i][0]} -> {weeks[i+1][0]}"

    def test_get_total_date_range(self):
        """測試總日期範圍"""
        start, end = get_total_date_range()
        assert isinstance(start, date)
        assert isinstance(end, date)
        assert start < end

    def test_get_total_date_range_matches_weeks(self):
        """測試總日期範圍與週範圍一致"""
        weeks = get_week_ranges()
        start, end = get_total_date_range()

        assert start == weeks[0][1], "總開始日期應等於第一週的開始日期"
        assert end == weeks[-1][2], "總結束日期應等於最後一週的結束日期"

    def test_week_labels_format(self):
        """測試週標籤格式"""
        weeks = get_week_ranges()
        for week in weeks:
            label = week[3]
            assert "-" in label, f"週標籤應包含連字號: {label}"
            assert "週" in label, f"週標籤應包含'週'字: {label}"


# 如果直接執行此檔案，顯示測試資訊
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
