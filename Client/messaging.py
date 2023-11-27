# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 11:04
# @Author  : KuangRen777
# @File    : messaging.py
# @Tags    :
import socket
import threading
from utils.encryption import Encryption  # 修改导入语句
from config import ENCRYPTION_KEY
import sys, ast
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from Server.database import Database
from datetime import datetime
import pytz
from PyQt5.QtCore import pyqtSignal, QObject

from Client.gui import GUI


class LoginException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ClientSignals(QObject):
    friendRequestResponse = pyqtSignal(str, str)
    new_message_received = pyqtSignal(str)
    display_error_message = pyqtSignal(str)
    update_list_item_message_preview_when_receive = pyqtSignal(int, str, str, bool)
    display_group_message = pyqtSignal(int, int, str, datetime)
    display_current_group_message = pyqtSignal(int, int, str, datetime)
    receive_friend_request = pyqtSignal(int, str, str)
    update_list_item_message_preview = pyqtSignal(int, str, str)
    display_message = pyqtSignal(int, str, datetime)
    run = pyqtSignal()


class Client:
    def __init__(self, host, port, user_info):
        self.host: str = host
        self.port: int = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.encryption = Encryption(key=ENCRYPTION_KEY)
        self.connected: bool = False

        self.signals = ClientSignals()
        self.signals.friendRequestResponse.connect(self.show_add_friend_response_dialog)

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

        # self.gui.signals.check_friend_requests.connect(self.check_friend_requests)
        # self.gui.signals.send_add_friend_request.connect(self.send_add_friend_request)
        # self.gui.signals.create_group.connect(self.create_group)
        # self.gui.signals.get_friend_info.connect(self.get_friend_info)
        # self.gui.signals.delete_friend.connect(self.delete_friend)
        # self.gui.signals.get_friend_list.connect(self.get_friend_list)
        # self.gui.signals.get_group_list.connect(self.get_group_list)
        # self.gui.signals.get_friend_name.connect(self.get_friend_name)
        # self.gui.signals.get_group_name.connect(self.get_group_name)
        # self.gui.signals.send_message.connect(self.send_message)
        # self.gui.signals.accept_friend_request.connect(self.accept_friend_request)
        # self.gui.signals.reject_friend_request.connect(self.reject_friend_request)

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

    def create_group(self, selected_friends_names, group_name):
        """
        向服务器发送创建群聊的请求。
        :param selected_friends_names: 选中的好友名称列表
        :param group_name: 群聊的名称
        """
        if self.connected:
            try:
                print(selected_friends_names)
                # 构造请求消息
                friends_names_str = ",".join(map(str, selected_friends_names))  # 将 ID 列表转换为字符串
                print(friends_names_str)
                create_group_message = f'create_group#$#{self.user_id}#$#{group_name}#$#{friends_names_str}'
                encrypted_message = self.encryption.encrypt(create_group_message.encode('utf-8'))
                self.socket.sendall(encrypted_message)
                print(f"Sent create group request to the server: {create_group_message}")
            except Exception as e:
                print(f"Failed to send create group request: {e}")

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
                    self.signals.display_error_message.emit(
                        '[OFF-LINE] Another user logged in with your user ID. You have '
                        'been disconnected.')
                    self.connected = False
                    raise LoginException('[OFF-LINE] Another user logged in with your user ID. You have been '
                                         'disconnected.')

                current_datetime = datetime.now(pytz.timezone('Asia/Shanghai'))

                parameter = message.split('#$#')
                message_type = parameter[0]

                if len(parameter) == 2:

                    if message_type == 'group_info_response':
                        group_info = parameter[1]
                        group_info = ast.literal_eval(group_info)
                        self.gui.display_group_info_signal.emit(group_info)

                elif len(parameter) == 3:

                    if message_type == 'group':
                        sender, content = parameter[1], parameter[2]
                        group_id, sender_id = sender.split('###')
                        group_name = self.get_group_name(int(group_id))
                        sender_name = self.get_friend_name(int(sender_id))

                        # 更新群组消息预览
                        self.signals.update_list_item_message_preview_when_receive.emit(int(group_id), content, sender_name,
                                                                                        True)

                        # 检查是否是当前查看的群组
                        if self.gui.current_item == int(group_id) and self.gui.current_chat_type == 'group':
                            formatted_message = f"{content}"
                            self.signals.display_group_message.emit(int(group_id), int(sender_id), formatted_message,
                                                                    current_datetime)
                        else:
                            formatted_message = f"{content}"
                            self.signals.display_current_group_message.emit(int(group_id), int(sender_id),
                                                                            formatted_message,
                                                                            current_datetime)

                    # elif message_type == 'friend_request':
                    #     # 假设消息格式是：friend_request#$#<user_id>#$#<friend_id>
                    #     user_id, friend_id = content.split('#$#')
                    #     self.gui.receive_friend_request(user_id, friend_id)

                    elif message_type == 'add_friend_response':
                        """
                        请求成功: add_friend_response#$#success#$#{friend_user_id}
                        请求失败: add_friend_response#$#fail#$#{friend_user_id}
                        好友 user_id 无效: add_friend_response#$#error#{friend_user_id}
                        """
                        response_type, friend_user_id = parameter[1], parameter[2]
                        self.signals.friendRequestResponse.emit(response_type, friend_user_id)
                        print(f'Receive server friend request reply: {message}')

                    elif message_type == 'check_requester_response':
                        print(f'Getting a response from the server to check for friends: {message}')
                        requester_id, requester_username = parameter[1], parameter[2]
                        # print(type(self.user_id), self.user_id)
                        # print(type(requester_id), requester_id)
                        # print(type(requester_username), requester_username)

                        self.signals.receive_friend_request.emit(self.user_id, requester_id, requester_username)

                    else:
                        sender, content = parameter[1], parameter[2]
                        sender_name = self.get_friend_name(int(sender))
                        # 更新好友消息预览
                        self.signals.update_list_item_message_preview.emit(int(sender), content, sender_name)

                        sender_name = "你" if sender == self.user_id else sender_name

                        # 检查是否是当前查看的好友
                        if self.gui.current_item == int(sender) and self.gui.current_chat_type == 'friend':

                            formatted_message = f"{sender_name}: {content}"
                            self.signals.display_message.emit(int(sender), formatted_message, current_datetime)

                        else:
                            formatted_message = f"<b>{sender_name}: {content}</b>"
                            self.signals.display_message.emit(int(sender), formatted_message, current_datetime)

            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def start(self):
        if self.connect_to_server():
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.signals.run.emit()
            sys.exit(self.app.exec_())  # 启动事件循环

    def get_group_info(self, group_id):
        # 向服务器发送获取群聊信息的请求
        request_message = f'get_group_info#$#{group_id}'
        encrypted_request = self.encryption.encrypt(request_message.encode('utf-8'))
        self.socket.sendall(encrypted_request)

        # # 等待并处理服务器返回的响应
        # encrypted_response = self.socket.recv(1024)
        # response_message = self.encryption.decrypt(encrypted_response).decode('utf-8')
        # if response_message.startswith('group_info_response'):
        #     _, group_info = response_message.split('#$#', 1)
        #     return eval(group_info)  # 将字符串转换为字典
        # else:
        #     print("Failed to get group info")
        #     return None

    def show_add_friend_response_dialog(self, response_type, friend_user_id):
        """
        显示添加好友请求的响应提示。
        """
        if response_type == 'success':
            message = f"成功申请添加用户 {friend_user_id} 为好友。"
            QMessageBox.information(None, "添加好友", message)
        elif response_type == 'fail':
            message = f"无法申请添加用户 {friend_user_id} 为好友。"
            QMessageBox.warning(None, "添加好友", message)
        elif response_type == 'error':
            message = f"用户 ID {friend_user_id} 无效，无法添加为好友。"
            QMessageBox.critical(None, "添加好友", message)

    # def send_friend_request(self, friend_id):
    #     """
    #     发送好友请求到服务器。
    #     """
    #     request_message = f'friend_request#$#{friend_id}'
    #     encrypted_request = self.encryption.encrypt(request_message)
    #     self.socket.sendall(encrypted_request)

    # def handle_friend_request_response(self, response):
    #     """
    #     处理服务器返回的好友请求响应。
    #     """
    #     # 假设响应格式为: 'friend_request_response#$#<result>'
    #     result = response.split('#$#')[1]
    #     if result == 'success':
    #         print("好友请求发送成功。")
    #     else:
    #         print("好友请求发送失败。")

    def accept_friend_request(self, requester_id):
        """
        接受好友请求。
        """
        accept_message = f'accept_friend_request#$#{requester_id}#$#{self.user_id}'
        encrypted_accept = self.encryption.encrypt(accept_message)
        self.socket.sendall(encrypted_accept)

    def reject_friend_request(self, requester_id):
        """
        拒绝好友请求。
        """

        reject_message = f'reject_friend_request#$#{requester_id}'
        encrypted_reject = self.encryption.encrypt(reject_message)
        self.socket.sendall(encrypted_reject)

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

    def send_add_friend_request(self, friend_user_id):
        # 发送添加朋友请求到服务器的逻辑
        if self.connected:
            try:
                # 构造请求消息
                request_message = f'friend_request#$#{self.user_id}#$#{friend_user_id}'
                encrypted_request = self.encryption.encrypt(request_message)
                self.socket.sendall(encrypted_request)
                print(f'Sends an add request to the server:{request_message}')
            except Exception as e:
                print(f"Failed to send add friend request: {e}")

    def check_friend_requests(self):
        # 向服务器发送请求检查好友请求的消息
        request_message = f"check_requester_requests#$#{self.user_id}"
        self.socket.send(self.encryption.encrypt(request_message.encode('utf-8')))
        print(f'Sends a check friend request to the server: {request_message}')


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
