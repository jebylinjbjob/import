"""
HireMe 單元測試
測試核心功能函式
"""

import pytest
from datetime import date, datetime
from hireme import is_email_format, count_users_by_week


class TestEmailValidation:
    """測試 email 格式驗證功能"""

    def test_valid_email_basic(self):
        """測試基本有效的 email 格式"""
        assert is_email_format("test@example.com") == True
        assert is_email_format("user@company.com.tw") == True
        assert is_email_format("admin@test.org") == True

    def test_valid_email_with_dots(self):
        """測試包含點號的有效 email"""
        assert is_email_format("first.last@example.com") == True
        assert is_email_format("user.name@company.co.uk") == True

    def test_valid_email_with_numbers(self):
        """測試包含數字的有效 email"""
        assert is_email_format("user123@example.com") == True
        assert is_email_format("test2023@company.com") == True

    def test_valid_email_with_special_chars(self):
        """測試包含特殊字元的有效 email"""
        assert is_email_format("user+tag@example.com") == True
        assert is_email_format("user_name@example.com") == True
        assert is_email_format("user-name@example.com") == True

    def test_invalid_email_no_at(self):
        """測試缺少 @ 符號的無效 email"""
        assert is_email_format("invalidemail.com") == False
        assert is_email_format("user.example.com") == False

    def test_invalid_email_no_domain(self):
        """測試缺少網域的無效 email"""
        assert is_email_format("user@") == False
        assert is_email_format("@example.com") == False

    def test_invalid_email_no_tld(self):
        """測試缺少頂級網域的無效 email"""
        assert is_email_format("user@example") == False

    def test_invalid_email_empty(self):
        """測試空字串和 None"""
        assert is_email_format("") == False
        assert is_email_format(None) == False

    def test_invalid_email_spaces(self):
        """測試包含空格的無效 email"""
        assert is_email_format("user @example.com") == False
        assert is_email_format("user@exam ple.com") == False


class TestUserCounting:
    """測試用戶週統計功能"""

    def test_count_users_in_week_range(self):
        """測試統計週區間內的用戶"""
        users = [
            {'CreateDate': date(2025, 11, 20)},
            {'CreateDate': date(2025, 11, 22)},
            {'CreateDate': date(2025, 11, 25)},
        ]

        # 11/17-11/23 應該有 2 位用戶
        count = count_users_by_week(users, date(2025, 11, 17), date(2025, 11, 23))
        assert count == 2

    def test_count_users_empty_list(self):
        """測試空用戶列表"""
        users = []
        count = count_users_by_week(users, date(2025, 11, 17), date(2025, 11, 23))
        assert count == 0

    def test_count_users_no_match(self):
        """測試沒有符合區間的用戶"""
        users = [
            {'CreateDate': date(2025, 10, 15)},
            {'CreateDate': date(2025, 12, 1)},
        ]
        count = count_users_by_week(users, date(2025, 11, 17), date(2025, 11, 23))
        assert count == 0

    def test_count_users_all_in_range(self):
        """測試所有用戶都在區間內"""
        users = [
            {'CreateDate': date(2025, 11, 17)},
            {'CreateDate': date(2025, 11, 20)},
            {'CreateDate': date(2025, 11, 23)},
        ]
        count = count_users_by_week(users, date(2025, 11, 17), date(2025, 11, 23))
        assert count == 3

    def test_count_users_boundary_dates(self):
        """測試邊界日期"""
        users = [
            {'CreateDate': date(2025, 11, 17)},  # 開始日
            {'CreateDate': date(2025, 11, 23)},  # 結束日
        ]
        count = count_users_by_week(users, date(2025, 11, 17), date(2025, 11, 23))
        assert count == 2

    def test_count_users_with_datetime(self):
        """測試 datetime 格式的日期"""
        users = [
            {'CreateDate': datetime(2025, 11, 20, 10, 30, 0)},
            {'CreateDate': datetime(2025, 11, 22, 14, 45, 30)},
        ]
        count = count_users_by_week(users, date(2025, 11, 17), date(2025, 11, 23))
        assert count == 2

    def test_count_users_with_string_date(self):
        """測試字串格式的日期"""
        users = [
            {'CreateDate': "2025-11-20"},
            {'CreateDate': "2025-11-22"},
        ]
        count = count_users_by_week(users, date(2025, 11, 17), date(2025, 11, 23))
        assert count == 2

    def test_count_users_mixed_date_formats(self):
        """測試混合日期格式"""
        users = [
            {'CreateDate': date(2025, 11, 20)},
            {'CreateDate': datetime(2025, 11, 21, 10, 0, 0)},
            {'CreateDate': "2025-11-22"},
        ]
        count = count_users_by_week(users, date(2025, 11, 17), date(2025, 11, 23))
        assert count == 3

    def test_count_users_with_none_date(self):
        """測試包含 None 日期的用戶"""
        users = [
            {'CreateDate': date(2025, 11, 20)},
            {'CreateDate': None},
            {'CreateDate': date(2025, 11, 22)},
        ]
        count = count_users_by_week(users, date(2025, 11, 17), date(2025, 11, 23))
        assert count == 2

    def test_count_users_across_year_boundary(self):
        """測試跨年度統計"""
        users = [
            {'CreateDate': date(2025, 12, 30)},
            {'CreateDate': date(2026, 1, 2)},
            {'CreateDate': date(2026, 1, 4)},
        ]
        count = count_users_by_week(users, date(2025, 12, 29), date(2026, 1, 4))
        assert count == 3


class TestDataStructure:
    """測試資料結構相關功能"""

    def test_user_dict_structure(self):
        """測試用戶資料字典結構"""
        user = {
            'Id': 'user123',
            'LoginName': 'test@example.com',
            'CreateDate': date(2025, 11, 20),
            'NameC': '測試用戶'
        }

        assert 'Id' in user
        assert 'LoginName' in user
        assert 'CreateDate' in user
        assert 'NameC' in user
        assert isinstance(user['CreateDate'], date)


# 如果直接執行此檔案，顯示測試資訊
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
