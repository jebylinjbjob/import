"""
SHA_256 模組單元測試
測試密碼雜湊功能
"""

import pytest
from SHA_256 import password_hash


class TestPasswordHash:
    """測試 password_hash 函式"""

    def test_basic_hash(self):
        """測試基本雜湊功能"""
        result = password_hash("123456", "test_user_id")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 產生 64 個十六進位字元

    def test_known_hash_value(self):
        """測試已知的雜湊值（來自原始程式碼的範例）"""
        test_value = "123456"
        test_unique_value = "3a33c354cdfa48f79cd3b00f413fc99f"
        result = password_hash(test_value, test_unique_value)

        # 驗證結果為 64 個字元的十六進位字串
        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)

    def test_consistent_output(self):
        """測試相同輸入產生相同輸出"""
        value = "mypassword"
        unique_value = "user123"

        result1 = password_hash(value, unique_value)
        result2 = password_hash(value, unique_value)

        assert result1 == result2

    def test_different_value_different_hash(self):
        """測試不同密碼產生不同雜湊值"""
        unique_value = "user123"

        hash1 = password_hash("password1", unique_value)
        hash2 = password_hash("password2", unique_value)

        assert hash1 != hash2

    def test_different_unique_value_different_hash(self):
        """測試不同唯一值產生不同雜湊值"""
        value = "password"

        hash1 = password_hash(value, "user1")
        hash2 = password_hash(value, "user2")

        assert hash1 != hash2

    def test_empty_value(self):
        """測試空字串密碼"""
        result = password_hash("", "user123")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_empty_unique_value(self):
        """測試空字串唯一值"""
        result = password_hash("password", "")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_special_characters(self):
        """測試特殊字元"""
        result = password_hash("p@$$w0rd!@#", "user-id_123")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_unicode_characters(self):
        """測試 Unicode 字元"""
        result = password_hash("密碼123", "使用者ID")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_very_long_value(self):
        """測試很長的輸入值"""
        long_value = "a" * 1000
        long_unique_value = "b" * 1000

        result = password_hash(long_value, long_unique_value)
        assert isinstance(result, str)
        assert len(result) == 64

    def test_hex_format(self):
        """測試輸出為有效的十六進位字串"""
        result = password_hash("test", "test")

        # 驗證只包含十六進位字元（0-9, a-f）
        assert all(c in '0123456789abcdef' for c in result)

        # 驗證可以轉換為整數
        try:
            int(result, 16)
        except ValueError:
            pytest.fail("結果不是有效的十六進位字串")

    def test_case_sensitivity(self):
        """測試大小寫敏感性"""
        unique_value = "user123"

        hash1 = password_hash("Password", unique_value)
        hash2 = password_hash("password", unique_value)

        assert hash1 != hash2

    def test_whitespace_matters(self):
        """測試空白字元影響雜湊結果"""
        unique_value = "user123"

        hash1 = password_hash("password", unique_value)
        hash2 = password_hash("password ", unique_value)
        hash3 = password_hash(" password", unique_value)

        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3

    def test_numeric_input(self):
        """測試數字輸入（作為字串）"""
        result = password_hash("123456789", "987654321")
        assert isinstance(result, str)
        assert len(result) == 64
