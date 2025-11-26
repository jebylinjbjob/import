"""
加密相關 (複製 HireMe 專案)
"""

import hashlib
from typing import Optional


def password_hash(value: str, unique_value: str, salt: Optional[str] = "moremoreSalt") -> str:
    """
    使用 SHA256 對密碼進行雜湊

    Args:
        value: 原始值（通常是密碼）
        unique_value: 唯一值（通常是使用者 ID 或其他唯一識別碼）
        salt: 鹽值（預設: "moremoreSalt"）

    Returns:
        SHA256 雜湊後的十六進位字串
    """
    # 組合字串：{value}-{uniqueValue}-moremoreSalt
    real_target = f"{value}-{unique_value}-moremoreSalt"

    # 使用 SHA256 進行雜湊
    hash_obj = hashlib.sha256()
    hash_obj.update(real_target.encode('utf-8'))
    result = hash_obj.hexdigest()

    return result


if __name__ == "__main__":
    # 測試範例
    test_value = "jebylin"
    test_unique_value = "7c3257b9adf0462aa3072bf0e75f3675"

    hashed = password_hash(test_value, test_unique_value)
    print(f"原始值: {test_value}")
    print(f"唯一值: {test_unique_value}")
    print(f"SHA256 雜湊結果: {hashed}")
