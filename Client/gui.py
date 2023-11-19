# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : gui.py
# @Tags    :
from PyQt5 import QtWidgets, QtGui, QtCore
from datetime import datetime


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
        for friend in self.client.all_friends:
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
        # 如果没有选择好友，不执行发送操作
        if self.current_friend is None:
            # 显示提示消息，这里可以根据实际情况调整
            QtWidgets.QMessageBox.warning(self, "提示", "请先选择一个好友")
            return

        message = self.message_entry.text()
        # 确保消息非空
        if message:
            self.client.send_message(self.current_friend, message)

            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

            self.display_message(f"{formatted_datetime} 你: {message}")
            self.message_entry.clear()

    def on_friend_clicked(self, index):
        friend_name = self.friends_list.currentItem().text()
        friend_id = self.get_friend_id(friend_name)  # 假设这个方法能够根据好友名获取其 user_id
        self.current_friend = friend_id  # 更新当前聊天的好友ID
        self.current_friend_label.setText(f"正在与 {friend_name} 聊天")  # 更新标签
        self.messages_area.clear()  # 清空聊天记录

        # 加载与该好友的聊天记录
        chat_messages = self.client.database.get_chat_messages(self.client.user_id, friend_id)
        for content, sender_id, timestamp in chat_messages:
            sender_name = "你" if sender_id == self.client.user_id else friend_name
            self.messages_area.append(f"{timestamp} {sender_name}: {content}")

    def get_friend_id(self, friend_name):
        for friend in self.client.all_friends:
            if friend[1] == friend_name:
                return friend[0]
        return None

    def run(self):
        self.show()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    client = Client()  # 应传入实际的 Client 对象
    gui = GUI(client)
    gui.run()
    sys.exit(app.exec_())
