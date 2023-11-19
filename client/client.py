# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:22
# @Author  : KuangRen777
# @File    : client.py
# @Tags    :
import socket
import threading
import sys
from client.gui import GUI
from client.chat import Chat  # 导入Chat类
from client.messaging import Client  # 导入 Client 类

if __name__ == "__main__":
    host = "127.0.0.1"  # 可以替换为实际的服务器地址
    port = 8000  # 可以替换为实际的服务器端口
    client = Client(host, port)
    client.start()
