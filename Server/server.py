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
                    """
                    上线消息，格式：#@#<user_id>
                    """
                    user_id = message[3:]
                    if user_id in self.current_online_id_to_address:
                        old_address = self.current_online_id_to_address[user_id]
                        old_socket = self.clients[old_address]
                        self.notify_disconnection(old_socket)  # 通知旧连接
                        old_socket.close()  # 关闭旧连接
                        self.remove_client(old_address)  # 移除旧连接信息
                    self.current_online_id_to_address[user_id] = address
                    self.current_online_address_to_id[address] = user_id
                    self.clients[address] = client_socket  # 更新为新连接
                    print(f'current online:{self.current_online_id_to_address}')

                else:

                    message_type, recipient, content = message.split('#$#')

                    if message_type == 'group':
                        """
                        群组消息，格式：group#$#<group_id>#$#<message_content>
                        """
                        self.handle_group_message(client_socket, recipient, content)

                    else:
                        """
                        个人消息，格式：private#$#<receiver_id>#$#<content>
                        """
                        sender_id = self.current_online_address_to_id[address]
                        receiver_id = recipient
                        content = content

                        self.database.add_chat_message(
                            sender_id=sender_id,
                            receiver_id=receiver_id,
                            content=content
                        )

                        if receiver_id in self.current_online_id_to_address:

                            print(f'[info] Send message to client # sender_id:{sender_id},'
                                  f'receiver_id:{receiver_id}, message:{message}.', end='')
                            self.send_message_to_client(
                                sender_id=sender_id,
                                receiver_id=receiver_id,
                                message=content
                            )
                            print('Done.')

            except socket.error:
                break

        client_socket.close()
        self.remove_client(address)

    def notify_disconnection(self, client_socket):
        """
        通知客户端其它地方有新的登录，这个连接将被断开。
        """
        try:
            disconnect_message = "##@@##OffsiteLogin##@##"
            encrypted_message = self.encryption.encrypt(disconnect_message.encode('utf-8'))
            client_socket.send(encrypted_message)
            print(f"Notified client of disconnection.")
        except socket.error as e:
            print(f"Error notifying client of disconnection: {e}")

    def remove_client(self, address):
        if address in self.current_online_address_to_id:
            user_id = self.current_online_address_to_id[address]
            del self.current_online_id_to_address[user_id]
            del self.current_online_address_to_id[address]
            del self.clients[address]

    def send_message_to_client(self, sender_id, receiver_id, message):
        try:
            if receiver_id in self.current_online_id_to_address:
                receiver_address = self.current_online_id_to_address[receiver_id]
                receiver_socket = self.clients[receiver_address]
                message = f'private#$#{sender_id}#$#{message}'
                receiver_socket.send(self.encryption.encrypt(message.encode('utf-8')))
            else:
                print(f'{receiver_id} Offline')
        except socket.error as e:
            print(f'[info] send_message_to_client error as {e}')

    def handle_group_message(self, client_socket, recipient, content):
        # 假设消息格式是：#$#group#$#<group_id>#$#<message_content>
        group_id = recipient
        sender_id = self.current_online_address_to_id[client_socket.getpeername()]

        # 将消息保存到数据库
        self.database.add_chat_message(sender_id, group_id, content, is_group=True)

        # 获取群组成员并转发消息
        group_members = self.database.get_group_members(group_id)
        for member_id in group_members:
            if str(member_id) != sender_id and str(member_id) in self.current_online_id_to_address:
                receiver_socket = self.clients[self.current_online_id_to_address[str(member_id)]]
                group_message = f'group#$#{group_id}###{sender_id}#$#{content}'
                receiver_socket.send(self.encryption.encrypt(group_message.encode('utf-8')))


if __name__ == "__main__":
    server = Server("127.0.0.1", 8000)
    server.start()
