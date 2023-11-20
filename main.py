# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:21
# @Author  : KuangRen777
# @File    : main.py
# @Tags    :
# conda activate yunliaojie
# cd C:\Users\luomi\PycharmProjects\YunLiaoJie
# python main.py Client
# python main.py Server
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
from Server.server import Server
from Client.client import Client
from Server.database import Database
from Server.authentication import Authentication
from Client.login_gui import LoginWindow
import config


def main():
    app = QApplication(sys.argv)

    if len(sys.argv) < 2:
        print("Usage: main.py <server/client>")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == 'server':
        server = Server(config.SERVER_HOST, config.SERVER_PORT)
        server.start()
    elif mode == 'client':
        db = Database()
        auth = Authentication(db)
        while True:
            login_window = LoginWindow(auth)
            result = login_window.exec_()  # 使用 exec_ 以模态方式运行
            if result == QDialog.Accepted:
                user_info = login_window.user_info
                client = Client(config.SERVER_HOST, config.SERVER_PORT, user_info)
                client.start()
                break
            elif result == QDialog.Rejected:
                response = QMessageBox.question(None, "重新登录", "登录失败或取消。您想要重试登录吗？",
                                                QMessageBox.Yes | QMessageBox.No)
                if response == QMessageBox.No:
                    break
    else:
        print("Invalid mode. Use 'server' or 'client'.")
        sys.exit(1)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
