# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : gui.py
# @Tags    :
from PyQt5 import QtWidgets, QtCore


class GUI(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("云聊界客户端")

        # 创建布局
        layout = QtWidgets.QVBoxLayout()

        # 创建消息显示区域
        self.messages_area = QtWidgets.QTextEdit(self)
        self.messages_area.setReadOnly(True)
        layout.addWidget(self.messages_area)

        # 创建消息输入框和发送按钮
        self.message_entry = QtWidgets.QLineEdit(self)
        send_button = QtWidgets.QPushButton("发送", self)
        send_button.clicked.connect(self.on_send_button_click)

        # 水平布局用于消息输入框和发送按钮
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.message_entry)
        hbox.addWidget(send_button)

        layout.addLayout(hbox)
        self.setLayout(layout)

    def display_message(self, message):
        self.messages_area.append(message)

    def on_send_button_click(self):
        message = self.message_entry.text()
        self.client.send_message(message)
        self.message_entry.clear()

    def run(self):
        self.show()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    gui = GUI(None)  # 正常情况下应该传入一个 Client 对象
    gui.run()
    sys.exit(app.exec_())
