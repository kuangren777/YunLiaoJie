# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 11:04
# @Author  : KuangRen777
# @File    : messaging.py
# @Tags    :
import socket
import threading

from client.gui import GUI


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui = GUI(self)  # 假设您有一个图形界面类 GUI
        self.chat = Chat(self)  # 创建一个Chat实例并关联到Client
        self.connected = False  # 添加一个连接状态标志

    def connect_to_server(self):
        try:
            self.socket.connect((self.host, self.port))
            print("Connected to server.")
            self.connected = True  # 设置连接状态为 True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def send_message(self, message):
        if self.connected:  # 只有在连接成功后才发送消息
            try:
                self.socket.sendall(message.encode())
            except Exception as e:
                print(f"Failed to send message: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode()
                self.gui.display_message(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def start(self):
        if self.connect_to_server():
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.gui.run()

    def on_send_button_click(self, message):
        self.send_message(message)


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
