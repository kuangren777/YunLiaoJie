# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : authentication.py
# @Tags    :
import hashlib
from Server.database import Database


class Authentication:
    def __init__(self, database: Database):
        self.database = database

    def register_user(self, username, password, email):
        """
        注册新用户。
        """
        password_hash = self.hash_password(password)
        try:
            self.database.add_user(username, password_hash, email)
            return True
        except Exception as e:
            print(f"Registration error: {e}")
            return False

    def login_user(self, username, password):
        user_info = self.database.get_user_info(username)
        if user_info:
            stored_password_hash = user_info[2]  # 假设这是从数据库获取的信息
            if self.verify_password(password, stored_password_hash):
                return user_info  # 返回用户信息
        return None

    def hash_password(self, password):
        """
        对密码进行哈希处理。
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password, hash):
        """
        验证密码哈希是否匹配。
        """
        return self.hash_password(password) == hash


# 示例用法
if __name__ == "__main__":
    db = Database()
    auth = Authentication(db)

    # 注册用户
    auth.register_user("username", "password", "email@example.com")

    # 用户登录
    login_success = auth.login_user("username", "password")
    print("Login successful:", login_success)
