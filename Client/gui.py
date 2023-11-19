# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : gui.py
# @Tags    :
from PyQt5 import QtWidgets, QtGui, QtCore


class GUI(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.current_friend = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("云聊界客户端")
        self.setGeometry(100, 100, 800, 600)  # 设置窗口位置和大小

        # 总体布局
        layout = QtWidgets.QHBoxLayout()

        # 好友列表
        self.friends_list = QtWidgets.QListWidget()
        print(self.client.user_id)
        current_friends = self.client.get_friend_list()
        for friend in current_friends:
            self.friends_list.addItem(friend[1])

        self.friends_list.clicked.connect(self.on_friend_clicked)
        layout.addWidget(self.friends_list, 1)

        # 右侧布局
        right_layout = QtWidgets.QVBoxLayout()

        # 当前聊天好友的名称
        self.current_friend_label = QtWidgets.QLabel("选择一个好友以开始聊天")
        self.current_friend_label.setAlignment(QtCore.Qt.AlignCenter)
        self.current_friend_label.setFont(QtGui.QFont("Arial", 14))
        right_layout.addWidget(self.current_friend_label)

        # 消息显示区域
        self.messages_area = QtWidgets.QTextEdit()
        self.messages_area.setReadOnly(True)
        right_layout.addWidget(self.messages_area, 5)

        # 消息输入框和发送按钮
        self.message_entry = QtWidgets.QLineEdit()
        send_button = QtWidgets.QPushButton("发送")
        send_button.clicked.connect(self.on_send_button_click)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.message_entry, 4)
        bottom_layout.addWidget(send_button, 1)
        right_layout.addLayout(bottom_layout)

        layout.addLayout(right_layout, 4)

        self.setLayout(layout)

    def display_message(self, message):
        self.messages_area.append(message)

    def on_send_button_click(self):
        message = self.message_entry.text()
        self.client.send_message(message)
        self.display_message(f"你: {message}")
        self.message_entry.clear()

    def on_friend_clicked(self, index):
        friend_name = self.friends_list.currentItem().text()
        self.current_friend = friend_name  # 更新当前聊天的好友名
        self.current_friend_label.setText(f"正在与 {friend_name} 聊天")  # 更新标签
        self.messages_area.clear()  # 清空聊天记录
        # TODO: 加载与该好友的聊天记录

    def run(self):
        self.show()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    client = Client()  # 应传入实际的 Client 对象
    gui = GUI(client)
    gui.run()
    sys.exit(app.exec_())
