# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : network.py
# @Tags    :
import socket
import threading


class NetworkServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = []

    def start(self):
        print(f"Server started on {self.host}:{self.port}")
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Connection from {address}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                # 处理接收到的数据
            except socket.error as e:
                print(f"Socket error: {e}")
                break
        client_socket.close()

    def broadcast(self, message):
        for client in self.clients:
            try:
                client.send(message.encode())
            except socket.error:
                self.clients.remove(client)

    def stop(self):
        self.server_socket.close()


class NetworkClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            return True
        except socket.error as e:
            print(f"Connection error: {e}")
            return False

    def send(self, message):
        try:
            self.socket.send(message.encode())
        except socket.error as e:
            print(f"Send error: {e}")

    def receive(self):
        try:
            return self.socket.recv(1024).decode()
        except socket.error as e:
            print(f"Receive error: {e}")
            return None

    def close(self):
        self.socket.close()


# 示例用法
if __name__ == "__main__":
    server = NetworkServer("127.0.0.1", 8000)
    threading.Thread(target=server.start).start()

    # 客户端示例
    client = NetworkClient("127.0.0.1", 8000)
    if client.connect():
        client.send("Hello, Server!")
        response = client.receive()
        print("Received:", response)
        client.close()
