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
                print(f'Raw message: {encrypted_message}')
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

                    parameter = message.split('#$#')
                    print(parameter)
                    message_type = parameter[0]

                    if len(parameter) == 2:
                        if message_type == 'check_requester_requests':
                            """
                            同意好友请求，格式：check_requester_requests#$#<user_id>#$#_
                            """
                            print(f'Receive a friend request check from the client: {message}')

                            user_id = parameter[1]

                            pending_requests = self.database.get_pending_friend_requests(user_id)

                            for requester_id in pending_requests:
                                requester_username = self.database.get_user_info_by_id(requester_id)['用户名']
                                message = f'check_requester_response#$#{requester_id}#$#{requester_username}'
                                client_socket.sendall(self.encryption.encrypt(message.encode('utf-8')))
                                print(f'check_requester_response: {message}')

                        elif message_type == 'get_group_info':
                            group_id = parameter[1]
                            print(group_id)
                            group_info = self.get_group_info(group_id)
                            response_message = f'group_info_response#$#{group_info}'
                            print(f'group_info_response: {response_message}')
                            encrypted_response = self.encryption.encrypt(response_message.encode('utf-8'))
                            client_socket.sendall(encrypted_response)

                    elif len(parameter) == 3:
                        message_type, recipient, content = message.split('#$#')

                        if message_type == 'group':
                            """
                            群组消息，格式：group#$#<group_id>#$#<message_content>
                            """
                            print(f'Receives client message:{message}')
                            group_id, message_content = parameter[1], parameter[2]
                            self.handle_group_message(client_socket, group_id, message_content)

                        elif message_type == 'friend_request':
                            """
                            添加好友消息，格式：friend_request#$#<user_id>#$#<friend_id>
                            """
                            print(f'Receives client sending add request:{message}')
                            # 解析出用户ID和朋友的用户名
                            user_id, friend_id = parameter[1], parameter[2]

                            # 调用处理添加朋友请求的方法
                            self.process_add_friend_request(user_id, friend_id, client_socket)

                        # 处理接受和拒绝好友请求的逻辑
                        elif message_type == 'accept_friend_request':
                            """
                            同意好友请求，格式：accept_friend_request#$#<user_id>#$#<friend_id>
                            """
                            print(f'Receives a friend request acceptance from the client: {message}')
                            user_id, friend_id = parameter[1], parameter[2]

                            self.database.accept_friend_request(user_id, friend_id)

                        elif message_type == 'reject_friend_request':
                            """
                            同意好友请求，格式：reject_friend_request#$#<user_id>#$#<friend_id>
                            """
                            print(f'Receive a friend request rejection from the client: {message}')

                            user_id, friend_id = parameter[1], parameter[2]

                            self.database.accept_friend_request(user_id, friend_id)

                        else:

                            """
                            个人消息，格式：private#$#<receiver_id>#$#<content>
                            """
                            print(f'Receive a private message from the client: {message}')

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

                    elif len(parameter) == 4:

                        if message_type == 'create_group':
                            user_id, group_name, friends_names_str = parameter[1], parameter[2], parameter[3]
                            print(f'userid:{user_id}, group_name:{group_name}, friends_name:{friends_names_str}')
                            friends_names = friends_names_str.split(',')
                            self.create_group(user_id, group_name, friends_names)

            except socket.error:
                break

        client_socket.close()
        self.remove_client(address)

    def get_group_info(self, group_id):
        # 从数据库中获取群聊信息
        # 假设这个方法返回一个包含群聊信息的字典
        return self.database.get_group_info_include_members(group_id)

    def create_group(self, user_id, group_name, friends_names):
        """
        处理创建群聊的逻辑。
        :param user_id: 创建群聊的用户 ID
        :param group_name: 群聊的名称
        :param friends_names: 群聊成员的 username 列表
        """
        # 在数据库中创建群聊，并添加成员
        group_id = self.database.create_group(group_name, user_id)
        if group_id:
            self.database.add_member_to_group(group_id, user_id)
            for friend_name in friends_names:
                friend_id = self.database.get_user_info(friend_name)[0]
                self.database.add_member_to_group(group_id, friend_id)

            print(f"Group '{group_name}' created with ID {group_id}")

    def process_add_friend_request(self, user_id, friend_user_id, client_socket):
        # 直接检查 user_id 是否有效
        if self.database.is_user_id_valid(friend_user_id):
            # 添加好友关系到数据库
            if self.database.add_friend(user_id, friend_user_id):
                # 通知客户端添加成功
                success_message = f'add_friend_response#$#success#$#{friend_user_id}'
                client_socket.sendall(self.encryption.encrypt(success_message.encode('utf-8')))
                print(f'Notify the client that the request was sent successfully:{success_message}')
            else:
                # 通知客户端添加失败
                fail_message = f'add_friend_response#$#fail#$#{friend_user_id}'
                client_socket.sendall(self.encryption.encrypt(fail_message.encode('utf-8')))
                print(f'Notify the client that the request was sent fail:{fail_message}')
        else:
            # 好友 user_id 无效，通知客户端错误
            error_message = f'add_friend_response#$#error#$#{friend_user_id}'
            client_socket.sendall(self.encryption.encrypt(error_message.encode('utf-8')))
            print(f'Notify the client that the request was sent error:{error_message}')

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
