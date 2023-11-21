# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : database.py
# @Tags    :
import sqlite3
from datetime import datetime
import pytz


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
        self.cursor.execute("SELECT user_id, username, password_hash, email, last_login FROM users WHERE username = ?",
                            (username,))
        return self.cursor.fetchone()

    def get_user_info_by_id(self, user_id):
        """
        查询用户信息。
        """
        self.cursor.execute("SELECT user_id, username, password_hash, email, last_login FROM users WHERE user_id = ?",
                            (user_id,))
        user_id, username, password_hash, email, last_login = self.cursor.fetchone()
        return {
            '用户账号': user_id,
            '用户名': username,
            'E-mail': email,
            '最近上线': last_login,
        }

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
        try:
            self.cursor.execute(
                "INSERT INTO friends (user_id, friend_id, status, created_at) VALUES (?, ?, 'pending', datetime('now'))",
                (user_id, friend_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f'Database: accept_friend_request {e}')
            return False

    def accept_friend_request(self, user_id, friend_id):
        """
        接受好友请求。
        """
        try:
            self.cursor.execute("UPDATE friends SET status = 'accepted' WHERE user_id = ? AND friend_id = ?",
                                (user_id, friend_id))
            self.cursor.execute(
                "INSERT INTO friends (user_id, friend_id, status, created_at) VALUES (?, ?, 'accepted', datetime('now'))",
                (friend_id, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f'Database: accept_friend_request {e}')
            return False

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

    def get_friends(self, user_id):
        """
        获取指定用户的所有好友的 user_id。
        """
        self.cursor.execute("""
            SELECT friend_id FROM friends
            WHERE user_id = ? AND status = 'accepted'
            UNION
            SELECT user_id FROM friends
            WHERE friend_id = ? AND status = 'accepted'
        """, (user_id, user_id))
        return [row[0] for row in self.cursor.fetchall()]

    def get_friends_user_info(self, user_id):
        """
        根据 user_id 查询该用户所有好友的信息。
        """
        # 查询好友的 user_id
        self.cursor.execute(
            "SELECT friend_id FROM friends WHERE user_id = ? AND status = 'accepted'", (user_id,)
        )
        friends_ids: list = [friend_id[0] for friend_id in self.cursor.fetchall()]

        # 查询每个好友的用户信息
        friends_info: list = []
        for friend_id in friends_ids:
            self.cursor.execute(
                "SELECT user_id, username, email, last_login FROM users WHERE user_id = ?", (friend_id,)
            )
            friend_info: tuple = self.cursor.fetchone()
            if friend_info:
                friends_info.append(friend_info)

        return friends_info

    def add_chat_message(self, sender_id, receiver_id, content, is_group=False):
        """
        向 chat_messages 表中添加一条消息记录。
        """
        current_utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)  # 获取当前 UTC 时间
        formatted_time = current_utc_time.strftime('%Y-%m-%d %H:%M:%S')  # 格式化时间为字符串

        message_type = 'group' if is_group else 'private'
        self.cursor.execute(
            "INSERT INTO chat_messages (sender_id, receiver_id, message_type, content, timestamp) VALUES (?, ?, ?, ?, ?)",
            (sender_id, receiver_id, message_type, content, formatted_time)
        )
        self.conn.commit()

    def get_chat_messages(self, user_id, friend_id, message_type='private'):
        """
        获取两个用户之间的聊天记录。
        :param user_id: 用户的ID
        :param friend_id: 好友的ID
        :param message_type: 消息类型（默认为 'private'）
        :return: 聊天记录列表
        """
        self.cursor.execute("""
            SELECT content, sender_id, timestamp FROM chat_messages
            WHERE ((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?))
            AND message_type = ?
            ORDER BY timestamp ASC
        """, (user_id, friend_id, friend_id, user_id, message_type))
        return self.cursor.fetchall()

    def get_latest_message(self, user_id, friend_id):
        """
        获取两个用户之间的最新聊天记录。
        """
        self.cursor.execute("""
            SELECT content FROM chat_messages
            WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp DESC LIMIT 1
        """, (user_id, friend_id, friend_id, user_id))
        result = self.cursor.fetchone()
        return result[0] if result else ""

    # 在 Database 类中
    def get_latest_message_with_sender(self, user_id, friend_id):
        """
        获取两个用户之间的最新私人聊天记录及发送者。
        """
        self.cursor.execute("""
            SELECT content, sender_id FROM chat_messages
            WHERE ((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?))
            AND message_type = 'private'
            ORDER BY timestamp DESC LIMIT 1
        """, (user_id, friend_id, friend_id, user_id))
        result = self.cursor.fetchone()
        return result if result else ("", None)

    def create_group(self, group_name, created_by):
        """创建群组并返回群组ID"""
        self.cursor.execute(
            "INSERT INTO groups (group_name, created_by, created_at) VALUES (?, ?, datetime('now'))",
            (group_name, created_by)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def add_group_member(self, group_id, user_id):
        """添加用户到群组"""
        self.cursor.execute(
            "INSERT INTO group_members (group_id, user_id, joined_at) VALUES (?, ?, datetime('now'))",
            (group_id, user_id)
        )
        self.conn.commit()

    def get_group_messages(self, group_id):
        """
        获取群组消息。
        """
        self.cursor.execute("""
            SELECT content, sender_id, timestamp FROM chat_messages
            WHERE receiver_id = ?
            AND message_type = 'group'
            ORDER BY timestamp ASC
        """, (group_id,))
        return self.cursor.fetchall()

    def get_group_members(self, group_id):
        """获取群组成员"""
        self.cursor.execute("SELECT user_id FROM group_members WHERE group_id = ?", (group_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_group_info(self, group_id):
        """
        获取群组的基本信息。
        """
        self.cursor.execute("SELECT group_name, created_by FROM groups WHERE group_id = ?", (group_id,))
        return self.cursor.fetchone()

    def get_groups_user_in(self, user_id):
        """
        获取用户所在的所有群组信息。
        """
        self.cursor.execute("""
            SELECT g.group_id, g.group_name 
            FROM groups g
            JOIN group_members gm ON g.group_id = gm.group_id
            WHERE gm.user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def get_latest_group_message_with_sender(self, group_id):
        """
        获取指定群组中的最新消息及发送者。
        """
        # 查询最新的群聊消息及其发送者的ID
        self.cursor.execute("""
            SELECT cm.content, u.username 
            FROM chat_messages cm 
            JOIN users u ON cm.sender_id = u.user_id
            WHERE cm.receiver_id = ? AND cm.message_type = 'group'
            ORDER BY cm.timestamp DESC 
            LIMIT 1
        """, (group_id,))
        result = self.cursor.fetchone()
        return result if result else ("", "")

    def delete_friend_by_id(self, user_id, friend_id):
        # 这里写数据库删除逻辑，下面仅为示例
        try:
            with self.conn:
                self.cursor.execute("DELETE FROM friends WHERE user_id = ? AND friend_id = ?", (user_id, friend_id))
            return True
        except Exception as e:
            print(f"Error deleting friend: {e}")
            return False

    def is_user_id_valid(self, user_id):
        # 假设 self.conn 是数据库连接对象
        with self.conn:
            # 查询数据库中是否存在该 user_id
            self.cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)", (user_id,))
            return self.cursor.fetchone()[0]

    def get_pending_friend_requests(self, user_id):
        """
        获取与指定用户有待处理的好友请求。
        """
        self.cursor.execute("""
            SELECT user_id FROM friends
            WHERE friend_id = ? AND status = 'pending'
        """, (user_id,))

        # 获取结果并整理成一个单一的列表
        pending_requests = [row[0] for row in self.cursor.fetchall()]

        return pending_requests



# if __name__ == "__main__":
#     db = Database()
#     # db.create_tables()
#     # 测试数据库功能
#     user_id = 1  # 假设的 user_id
#     friends_ids = db.get_friends_user_info(user_id)
#     print(f"User {user_id}'s friends: {friends_ids}")

if __name__ == "__main__":
    db = Database()
    db.create_tables()

    # 添加一条聊天消息示例
    db.add_chat_message(1, 2, 'Hello, this is a message content')
    print("Message added to the database.")
