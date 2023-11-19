# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : Server.py
# @Tags    :
import socket
import threading
from Server.database import Database
from utils.encryption import Encryption
from config import ENCRYPTION_KEY


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))

        self.database = Database()  # 假设有一个数据库类处理数据库操作
        self.encryption = Encryption(key=ENCRYPTION_KEY)  # 创建加密实例
        self.current_online_id_to_address = {}
        self.current_online_address_to_id = {}
        self.clients = {}  # 用于存储客户端套接字和地址的映射

    def start(self):
        self.socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client_socket, address = self.socket.accept()
            self.clients[address] = client_socket  # 存储客户端套接字
            print(f"Connection from {address}")

            # 创建并启动新线程来处理客户端
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self, client_socket, address):
        while True:
            try:
                encrypted_message = client_socket.recv(1024)
                if not encrypted_message:
                    break
                message = self.encryption.decrypt(encrypted_message).decode('utf-8')

                print(f"Received message from {address}: {message}")

                if '#@#' in message:
                    user_id = message[3:]
                    self.current_online_id_to_address[user_id] = address
                    self.current_online_address_to_id[address] = user_id
                    print(f'current online:{self.current_online_id_to_address}')
                else:
                    message = message.split('#$#')
                    sender_id = self.current_online_address_to_id[address]
                    receiver_id = message[0]
                    content = message[1]

                    self.database.add_chat_message(
                        sender_id=sender_id,
                        receiver_id=receiver_id,
                        content=content
                    )

                    if receiver_id in self.current_online_id_to_address:
                        self.send_message_to_client(
                            receiver_id=receiver_id,
                            message=content
                        )

            except socket.error:
                break

        client_socket.close()
        self.remove_client(address)

    def remove_client(self, address):
        if address in self.current_online_address_to_id:
            user_id = self.current_online_address_to_id[address]
            del self.current_online_id_to_address[user_id]
            del self.current_online_address_to_id[address]
            del self.clients[address]

    def send_message_to_client(self, receiver_id, message):
        try:
            if receiver_id in self.current_online_id_to_address:
                receiver_address = self.current_online_id_to_address[receiver_id]
                receiver_socket = self.clients[receiver_address]
                receiver_socket.send(self.encryption.encrypt(message.encode('utf-8')))
            else:
                print(f'{receiver_id} Offline')
        except socket.error as e:
            print(f'[info] send_message_to_client error as {e}')


if __name__ == "__main__":
    server = Server("127.0.0.1", 8000)
    server.start()
