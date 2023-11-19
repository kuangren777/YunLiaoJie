# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : file_transfer.py
# @Tags    :
import os
import socket
import hashlib
from utils.encryption import Encryption


class FileTransfer:
    def __init__(self, client, server_host, server_port, file_dir="files/"):
        self.client = client
        self.server_host = server_host
        self.server_port = server_port
        self.file_dir = file_dir
        self.buffer_size = 1024

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

    def connect_to_server(self):
        self.file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.file_socket.connect((self.server_host, self.server_port))
            return True
        except Exception as e:
            print(f"File transfer connection failed: {e}")
            return False

    def send_file(self, file_path, resume=False):
        if not self.connect_to_server():
            return

        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        encrypted_file_name = Encryption().encrypt(file_name)  # 使用Encryption类的实例进行加密

        if resume:
            self.file_socket.sendall(f"RESUME,{encrypted_file_name}".encode())
        else:
            self.file_socket.sendall(f"{encrypted_file_name},{file_size}".encode())

        with open(file_path, "rb") as file:
            bytes_sent = 0

            if resume:
                server_response = self.file_socket.recv(1024).decode()
                if server_response.startswith("OK,"):
                    bytes_sent = int(server_response.split(",")[1])
                    file.seek(bytes_sent)

            while bytes_sent < file_size:
                bytes_read = file.read(self.buffer_size)
                encrypted_data = Encryption().encrypt(bytes_read)  # 使用Encryption类的实例进行加密
                self.file_socket.sendall(encrypted_data)
                bytes_sent += len(bytes_read)

        self.file_socket.close()

    def receive_file(self, file_path, resume=False):
        if not self.connect_to_server():
            return

        if resume:
            bytes_received = os.path.getsize(file_path)
            encrypted_info = f"RESUME,{Encryption().encrypt(os.path.basename(file_path))},{bytes_received}".encode()
            self.file_socket.sendall(encrypted_info)
        else:
            file_info = self.file_socket.recv(1024).decode()
            encrypted_file_name, file_size = file_info.split(',')
            file_name = Encryption().decrypt(encrypted_file_name)  # 使用Encryption类的实例进行解密
            file_path = os.path.join(self.file_dir, file_name)

        with open(file_path, "ab" if resume else "wb") as file:
            while True:
                encrypted_data = self.file_socket.recv(self.buffer_size)
                if not encrypted_data:
                    break
                data = Encryption().decrypt(encrypted_data)  # 使用Encryption类的实例进行解密
                file.write(data)

        self.file_socket.close()

    # ... 其他方法 ...
