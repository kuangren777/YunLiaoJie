# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : gui.py
# @Tags    :
from PyQt5 import QtWidgets, QtGui, QtCore
from datetime import datetime, timedelta
import pytz


class GUI(QtWidgets.QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.current_friend = None
        self.last_message_time = None  # 新增变量以存储上一条消息的时间戳
        self.init_ui()
        self.last_message_time_per_friend = {}  # 用于存储每个好友的最后消息时间戳

    def init_ui(self):
        # 假设 client 对象有一个 username 属性
        username = self.client.username if hasattr(self.client, 'username') else "未知用户"
        self.setWindowTitle(f"云聊界客户端 - {username}")

        self.setGeometry(100, 100, 800, 600)  # 设置窗口位置和大小

        # 总体布局为 Splitter，允许调节大小
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # 好友列表
        self.friends_list = QtWidgets.QListWidget()
        self.friends_list.setMinimumWidth(200)  # 设置最小宽度以确保可见性

        if not self.client.all_friends:
            print("好友列表为空。请确保有好友数据。")
        else:
            for friend in self.client.all_friends:
                friend_id, friend_name = friend[0], friend[1]
                latest_message, sender_id = self.client.database.get_latest_message_with_sender(self.client.user_id,
                                                                                                friend_id)
                prefix = "你:" if sender_id == self.client.user_id else "对方:"
                latest_message = f"{prefix}{latest_message[:5]}..." if len(latest_message) > 5 else latest_message

                # 创建自定义列表项
                item_widget = QtWidgets.QWidget()
                item_layout = QtWidgets.QVBoxLayout(item_widget)

                # 用户名加粗放大显示
                name_label = QtWidgets.QLabel(friend_name)
                name_label.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
                name_label.setObjectName(f"name_label_{friend_id}")  # 设置对象名称
                item_layout.addWidget(name_label)

                # 最近一条聊天记录小字显示
                message_label = QtWidgets.QLabel(latest_message)
                message_label.setFont(QtGui.QFont("Arial", 10))
                message_label.setObjectName(f"message_label_{friend_id}")  # 设置对象名称
                item_layout.addWidget(message_label)

                # 创建列表项，将自定义 widget 作为其子项
                item = QtWidgets.QListWidgetItem(self.friends_list)
                item.setSizeHint(item_widget.sizeHint())  # 重要：设置列表项的大小

                # 添加列表项到列表中
                self.friends_list.addItem(item)
                self.friends_list.setItemWidget(item, item_widget)

        # 连接点击信号到槽函数
        self.friends_list.itemClicked.connect(self.on_friend_clicked)

        # 将好友列表添加到 Splitter
        splitter.addWidget(self.friends_list)

        # 右侧布局
        right_widget = QtWidgets.QWidget()  # 右侧的 widget
        right_layout = QtWidgets.QVBoxLayout(right_widget)

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
        self.message_entry.returnPressed.connect(self.on_send_button_click)  # 绑定回车键

        send_button = QtWidgets.QPushButton("发送")
        send_button.clicked.connect(self.on_send_button_click)

        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addWidget(self.message_entry, 4)
        bottom_layout.addWidget(send_button, 1)
        right_layout.addLayout(bottom_layout)

        # 将右侧 widget 添加到 Splitter
        splitter.addWidget(right_widget)

        # 设置 Splitter 的拉伸比例，左侧为 1，右侧为 3
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        # 设置 Splitter 的最小尺寸，防止拖得太小
        splitter.setSizes([200, 600])

        # 设置 Splitter 作为主布局
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # 设置列表项间距
        self.friends_list.setSpacing(1)  # 设置列表项的间距，您可以调整数字来改变间距大小

    def display_message(self, sender_id, message, timestamp):
        last_time = self.last_message_time_per_friend.get(self.current_friend)
        if self.should_display_time(timestamp, last_time):
            self.messages_area.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

        # 检查消息发送者是否是当前选择的好友
        if sender_id != self.current_friend:
            message = f"<b>{message}</b>"

        self.messages_area.append(message)
        self.last_message_time = timestamp  # 更新上一条消息的时间戳

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.on_send_button_click()

    def display_message_normal(self, message, timestamp):
        # 获取当前聊天好友的最后一条消息时间戳
        last_time = self.last_message_time_per_friend.get(self.current_friend)

        # 检查是否需要显示时间
        if self.should_display_time(timestamp, last_time):
            self.messages_area.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

        self.messages_area.append(message)
        self.last_message_time_per_friend[self.current_friend] = timestamp  # 更新当前聊天好友的最后消息时间戳

    def on_send_button_click(self):
        # 如果没有选择好友，不执行发送操作
        if self.current_friend is None:
            QtWidgets.QMessageBox.warning(self, "提示", "请先选择一个好友")
            return

        message = self.message_entry.text().strip()
        # 确保消息非空
        if not message:
            return

        # 发送消息
        self.client.send_message(self.current_friend, message)

        # 获取当前时间，并转换为时区感知的 datetime 对象
        current_datetime = datetime.now(pytz.timezone('Asia/Shanghai'))

        # 显示消息，传递当前时间戳
        self.display_message_normal(f"你: {message}", current_datetime)

        # 清空消息输入框
        self.message_entry.clear()

        # 更新好友列表中的最新消息显示
        latest_message = (message[:5] + '...') if len(message) > 5 else message
        self.update_friend_list_with_latest_message(self.current_friend, latest_message, True)

    def on_friend_clicked(self, item):
        # 获取当前点击的列表项对应的自定义 widget
        item_widget = self.friends_list.itemWidget(item)
        # 通过 item_widget 中的子 widget（如 QLabel）获取数据
        friend_name = item_widget.findChild(QtWidgets.QLabel).text()
        friend_id = self.get_friend_id(friend_name)  # 假设这个方法能够根据好友名获取其 user_id
        self.current_friend = friend_id
        self.current_friend_label.setText(f"{friend_name}")
        self.messages_area.clear()

        # 获取当前好友的最后消息时间戳
        last_time = self.last_message_time_per_friend.get(friend_id)

        chat_messages = self.client.database.get_chat_messages(self.client.user_id, friend_id)
        for content, sender_id, timestamp in chat_messages:
            # 将 UTC 时间戳转换为本地时间
            utc_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))

            # 检查是否需要显示时间
            if self.should_display_time(local_time, last_time):
                self.messages_area.append(local_time.strftime('%Y-%m-%d %H:%M:%S'))

            # 格式化消息显示
            sender_name = "你" if int(sender_id) == self.client.user_id else friend_name
            formatted_message = f"{sender_name}: {content}"

            # 显示消息
            self.messages_area.append(formatted_message)

            # 更新当前好友的最后消息时间戳
            last_time = local_time

        # 更新该好友的最后消息时间戳
        self.last_message_time_per_friend[friend_id] = last_time

    def get_friend_id(self, friend_name):
        for friend in self.client.all_friends:
            if friend[1] == friend_name:
                return friend[0]
        return None

    def update_friend_list_with_latest_message(self, friend_id, latest_message, is_sender):
        # 遍历好友列表项
        for index in range(self.friends_list.count()):
            item = self.friends_list.item(index)
            widget = self.friends_list.itemWidget(item)

            # 使用对象名称查找 QLabel
            name_label = widget.findChild(QtWidgets.QLabel, f"name_label_{friend_id}")
            message_label = widget.findChild(QtWidgets.QLabel, f"message_label_{friend_id}")

            # 确保找到正确的 QLabel 并且它们的名称匹配
            if message_label:
                prefix = "你:" if is_sender else "对方:"
                # 更新最新消息显示
                message_label.setText(f"{prefix}{latest_message}")
                break  # 找到后退出循环

    def should_display_time(self, current_time, last_time):
        # 修改此方法以使用提供的 last_time
        if not last_time or (current_time - last_time) > timedelta(minutes=5):
            return True
        if last_time.date() != current_time.date():
            return True
        return False

    def run(self):
        self.show()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    client = Client()  # 应传入实际的 Client 对象
    gui = GUI(client)
    gui.run()
    sys.exit(app.exec_())
