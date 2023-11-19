# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : database.py
# @Tags    :
import sqlite3


class Database:
    def __init__(self, db_path='db/chat_database.sqlite'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """
        创建数据库表。
        """
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE,
                                password_hash TEXT,
                                email TEXT UNIQUE,
                                last_login DATETIME)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS friends (
                                relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                friend_id INTEGER,
                                status TEXT,
                                created_at DATETIME)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
                                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                sender_id INTEGER,
                                receiver_id INTEGER,
                                message_type TEXT,
                                content TEXT,
                                timestamp DATETIME)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS file_transfers (
                                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                sender_id INTEGER,
                                receiver_id INTEGER,
                                file_name TEXT,
                                file_size INTEGER,
                                transfer_status TEXT,
                                timestamp DATETIME)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS groups (
                                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                group_name TEXT,
                                created_by INTEGER,
                                created_at DATETIME)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS group_members (
                                membership_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                group_id INTEGER,
                                user_id INTEGER,
                                joined_at DATETIME)''')

        self.conn.commit()

    def add_user(self, username, password_hash, email):
        """
        添加新用户。
        """
        self.cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                            (username, password_hash, email))
        self.conn.commit()

    def get_user_info(self, username):
        """
        查询用户信息。
        """
        self.cursor.execute("SELECT user_id, username, email, last_login FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def update_user_status(self, user_id, status):
        """
        更新用户的在线状态。
        """
        self.cursor.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
        self.conn.commit()

    def add_friend(self, user_id, friend_id):
        """
        添加好友关系。
        """
        self.cursor.execute(
            "INSERT INTO friends (user_id, friend_id, status, created_at) VALUES (?, ?, 'pending', datetime('now'))",
            (user_id, friend_id))
        self.conn.commit()

    def accept_friend_request(self, user_id, friend_id):
        """
        接受好友请求。
        """
        self.cursor.execute("UPDATE friends SET status = 'accepted' WHERE user_id = ? AND friend_id = ?",
                            (friend_id, user_id))
        self.conn.commit()

    def reject_friend_request(self, user_id, friend_id):
        """
        拒绝好友请求。
        """
        self.cursor.execute("DELETE FROM friends WHERE user_id = ? AND friend_id = ?", (friend_id, user_id))
        self.conn.commit()

    def close(self):
        """
        关闭数据库连接。
        """
        self.conn.close()


if __name__ == "__main__":
    db = Database()
    db.create_tables()
    # 测试数据库功能
