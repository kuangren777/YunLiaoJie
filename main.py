# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:21
# @Author  : KuangRen777
# @File    : main.py
# @Tags    :
import sys
from Server.server import Server
from Client.client import Client
import config


# conda activate yunliaojie
# cd C:\Users\luomi\PycharmProjects\YunLiaoJie
# python main.py Client
# python main.py Server
from PyQt5.QtWidgets import QApplication, QDialog
from Server.database import Database
from Server.authentication import Authentication
from Client.login_gui import LoginWindow


def login():
    app = QApplication(sys.argv)

    # 这里假设您已经创建了 Authentication 实例
    db = Database()  # 假设数据库实例化
    auth = Authentication(db)

    login_window = LoginWindow(auth)

    login_window.exec_()  # 执行登录窗口并等待关闭
    user_info = login_window.user_info

    return user_info


def main():
    if len(sys.argv) < 2:
        print("Usage: main.py <server/client>")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == 'server':
        server = Server(config.SERVER_HOST, config.SERVER_PORT)
        server.start()
    elif mode == 'client':
        user_info = None
        while not user_info:
            user_info = login()

        client = Client(config.SERVER_HOST, config.SERVER_PORT, user_info)
        client.start()
    else:
        print("Invalid mode. Use 'server' or 'client'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
