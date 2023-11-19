# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : server.py
# @Tags    :
import socket
import threading
from server.database import Database
from utils.encryption import Encryption  # 修改导入语句


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.clients = {}  # 用于保存连接的客户端

        self.database = Database()  # 假设有一个数据库类处理数据库操作
        self.encryption = Encryption()  # 创建加密实例

    def start(self):
        self.socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, address = self.socket.accept()
            print(f"Connection from {address}")

            # 创建并启动新线程来处理客户端
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self, client_socket, address):
        while True:
            try:
                encrypted_message = client_socket.recv(1024)
                if not encrypted_message:
                    break
                message = self.encryption.decrypt(encrypted_message)
                print(message)
                # 处理解密后的消息

            except socket.error:
                print(11)
                break

        client_socket.close()
        self.remove_client(address)

    def remove_client(self, address):
        if address in self.clients:
            del self.clients[address]

    def send_message_to_client(self, client_socket, message):
        try:
            encrypted_message = self.encryption.encrypt(message)
            client_socket.send(encrypted_message)
        except socket.error:
            pass

    # ... 其他方法 ...


if __name__ == "__main__":
    server = Server("127.0.0.1", 8000)
    server.start()
