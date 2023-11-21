# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 11:04
# @Author  : KuangRen777
# @File    : messaging.py
# @Tags    :
import socket
import threading
from utils.encryption import Encryption  # 修改导入语句
from config import ENCRYPTION_KEY
import sys
from PyQt5 import QtWidgets, QtCore
from Server.database import Database
from datetime import datetime
import pytz

from Client.gui import GUI


class LoginException(Exception):
    def __init__(self, message):
        super().__init__(message)


class Client:
    def __init__(self, host, port, user_info):
        self.host: str = host
        self.port: int = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encryption = Encryption(key=ENCRYPTION_KEY)
        self.connected: bool = False

        self.app = QtWidgets.QApplication(sys.argv)  # 创建 QApplication 实例
        self.login_info: tuple = user_info
        self.user_id: int = user_info[0]
        self.username: str = user_info[1]
        self.database = Database()

        self.all_friends = self.get_friend_list()
        self.all_friends_id_to_name: dict = {}
        self.all_friends_name_to_id: dict = {}
        for friend in self.all_friends:
            self.all_friends_id_to_name[friend[0]] = friend[1]
            self.all_friends_name_to_id[friend[1]] = friend[0]

        self.all_groups = self.get_group_list()  # 获取群聊列表

        self.gui = GUI(self)  # 创建 GUI 实例
        self.chat = Chat(self)  # 创建 Chat 实例

    def connect_to_server(self):
        try:
            self.socket.connect((self.host, self.port))
            print("Connected to Server.")
            self.connected = True  # 设置连接状态为 True
            self.socket.sendall(self.encryption.encrypt(f'#@#{self.user_id}'))
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def send_message(self, recipient: str, message: str, is_group: bool = False):
        if self.connected:
            try:
                message_type = 'group' if is_group else 'private'
                message = f'{message_type}#$#{recipient}#$#{message}'
                encrypted_message = self.encryption.encrypt(message)
                self.socket.sendall(encrypted_message)
            except Exception as e:
                print(f"Failed to send message: {e}")

    def get_friend_name(self, friend_id: int):
        for friend in self.all_friends:
            if friend[0] == friend_id:
                return friend[1]
        return None

    def receive_messages(self):
        while self.connected:
            try:
                encrypted_message = self.socket.recv(1024)
                if not encrypted_message:
                    break

                message = self.encryption.decrypt(encrypted_message).decode('utf-8')
                if '##@@##OffsiteLogin##@##' in message:
                    self.gui.display_error_message('[OFF-LINE] Another user logged in with your user ID. You have '
                                                   'been disconnected.')
                    self.connected = False
                    raise LoginException('[OFF-LINE] Another user logged in with your user ID. You have been '
                                         'disconnected.')

                message_type, sender, content = message.split('#$#')

                current_datetime = datetime.now(pytz.timezone('Asia/Shanghai'))

                if message_type == 'group':
                    group_id, sender_id = sender.split('###')
                    group_name = self.get_group_name(int(group_id))
                    sender_name = self.get_friend_name(int(sender_id))

                    # 更新群组消息预览
                    self.gui.update_list_item_message_preview_when_receive(int(group_id), content, sender_name,
                                                                           is_group=True)

                    # 检查是否是当前查看的群组
                    if self.gui.current_item == int(group_id) and self.gui.current_chat_type == 'group':
                        formatted_message = f"{content}"
                        self.gui.display_group_message(int(group_id), int(sender_id), formatted_message,
                                                       current_datetime)
                    else:
                        formatted_message = f"{content}"
                        self.gui.display_current_group_message(int(group_id), int(sender_id), formatted_message,
                                                               current_datetime)
                else:
                    sender_name = self.get_friend_name(int(sender))
                    # 更新好友消息预览
                    self.gui.update_list_item_message_preview(int(sender), content, sender_name)

                    sender_name = "你" if sender == self.user_id else sender_name

                    # 检查是否是当前查看的好友
                    if self.gui.current_item == int(sender) and self.gui.current_chat_type == 'friend':

                        formatted_message = f"{sender_name}: {content}"
                        self.gui.display_message(int(sender), formatted_message, current_datetime)

                    else:
                        formatted_message = f"<b>{sender_name}: {content}</b>"
                        self.gui.display_message(int(sender), formatted_message, current_datetime)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def start(self):
        if self.connect_to_server():
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.gui.run()
            sys.exit(self.app.exec_())  # 启动事件循环

    def on_send_button_click(self, message: str):
        self.send_message(message)

    def get_friend_list(self):
        return self.database.get_friends_user_info(self.user_id)

    def add_message_into_database(self, sender_id, receiver_id, content):
        self.database.add_chat_message(sender_id, receiver_id, content)

    def get_group_list(self) -> [(int, str)]:
        return self.database.get_groups_user_in(self.user_id)

    def get_group_name(self, group_id):
        return self.database.get_group_info(group_id)[0]

    def get_friend_info(self, friend_id):
        # 假设 database 方法 get_friend_info_by_id 返回好友的详细信息
        return self.database.get_user_info_by_id(friend_id)

    def delete_friend(self, friend_id):
        # 这里应该实现删除好友的逻辑，例如调用数据库的方法
        # 假设 delete_friend_by_id 是在数据库操作类中实现的一个方法
        if self.database.delete_friend_by_id(self.user_id, friend_id):
            print(f"好友 {friend_id} 已被删除。")
            return True
        else:
            print(f"无法删除好友 {friend_id}。")
            return False


class Chat:
    def __init__(self, client):
        self.client = client
        self.chat_history = []
        self.current_chat_id = None  # 添加一个当前聊天对象的属性

    def send_message(self, message):
        """
        发送消息到服务器。
        """
        if message:
            formatted_message = self.format_message(message)
            self.client.send_message(formatted_message)
            self.chat_history.append((True, formatted_message))  # True 表示发送的消息

    def receive_message(self, message):
        """
        从服务器接收消息。
        """
        self.chat_history.append((False, message))  # False 表示接收的消息

    def format_message(self, message):
        """
        格式化消息。
        """
        # 这里可以添加更复杂的消息格式化逻辑
        return f"[User] {message}"

    def get_chat_history(self):
        """
        获取聊天记录。
        """
        return self.chat_history

    def clear_chat_history(self):
        """
        清除聊天记录。
        """
        self.chat_history.clear()

    def set_current_chat(self, chat_id):
        """
        设置当前聊天。
        """
        self.current_chat_id = chat_id
        # 这里可以根据 chat_id 实现切换聊天对象的逻辑


if __name__ == "__main__":
    client = Client("127.0.0.1", 8000)
    client.start()
