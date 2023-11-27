# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : gui.py
# @Tags    :
import time

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, QObject
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication

from Client.Dialog.CreateGroupDialog import CreateGroupDialog
from Client.Dialog.AddFriendDialog import AddFriendDialog
from Client.Dialog.AddGroupMemberDialog import AddGroupMemberDialog

import pytz
import threading
import time


class GUI(QtWidgets.QWidget):
    display_friend_info_signal = pyqtSignal(dict)
    display_group_info_signal = pyqtSignal(dict)
    display_group_add_member_list_signal = pyqtSignal(dict)
    friend_request_received = pyqtSignal(str, str, str)  # user_id, requester_id, requester_username

    def __init__(self, client):
        super().__init__()
        self.client = client
        self.info_dialog = None  # 初始化为 None
        self.current_item = None
        self.current_chat_type = None
        self.last_message_time = None
        self.init_ui()
        self.last_message_time_per_chat = {}  # 用于存储每个聊天对象（好友或群聊）的最后消息时间戳

        # 将信号连接到槽函数
        self.display_friend_info_signal.connect(self.show_friend_info)
        self.display_group_info_signal.connect(self.show_group_info)
        self.display_group_add_member_list_signal.connect(self.display_group_add_member_list)
        self.friend_request_received.connect(self.handle_friend_request_received)
        self.client.signals.display_error_message.connect(self.display_error_message)
        self.client.signals.update_list_item_message_preview_when_receive.connect(
            self.update_list_item_message_preview_when_receive)
        self.client.signals.display_group_message.connect(self.display_group_message)
        self.client.signals.display_current_group_message.connect(self.display_current_group_message)
        self.client.signals.receive_friend_request.connect(self.receive_friend_request)
        self.client.signals.update_list_item_message_preview.connect(self.update_list_item_message_preview)
        self.client.signals.display_message.connect(self.display_message)
        self.client.signals.run.connect(self.run)

    def init_ui(self):
        # 假设 client 对象有一个 username 属性
        username: str = self.client.username if hasattr(self.client, 'username') else "未知用户"
        self.setWindowTitle(f"云聊界客户端 - {username}")
        self.setGeometry(100, 100, 1000, 700)  # 设置窗口位置和大小

        # 总体布局为 Splitter，允许调节大小
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # 左侧布局
        left_widget = QtWidgets.QWidget()  # 创建一个新的 widget 用于左侧布局
        left_layout = QtWidgets.QVBoxLayout(left_widget)  # 左侧使用垂直布局

        # 在好友列表上方添加操作按钮
        top_layout = QtWidgets.QHBoxLayout()

        # 添加朋友按钮
        self.add_friend_button = QtWidgets.QPushButton("添加好友")
        self.add_friend_button.clicked.connect(self.on_add_friend_button_click)  # 需要定义该方法
        top_layout.addWidget(self.add_friend_button)

        # 好友验证
        self.friend_request = QtWidgets.QPushButton("好友验证")
        self.friend_request.clicked.connect(self.on_friend_request_button_click)  # 需要定义该方法
        top_layout.addWidget(self.friend_request)

        # 发起群聊按钮
        self.create_group_button = QtWidgets.QPushButton("发起群聊")
        self.create_group_button.clicked.connect(self.on_create_group_button_click)  # 需要定义该方法
        top_layout.addWidget(self.create_group_button)

        # 将顶部布局添加到左侧布局
        left_layout.addLayout(top_layout)

        # 好友列表
        self.friends_list = QtWidgets.QListWidget()
        self.friends_list.setMinimumWidth(200)
        left_layout.addWidget(self.friends_list)  # 将好友列表添加到左侧布局

        # 将左侧 widget 添加到 Splitter
        splitter.addWidget(left_widget)
        self.friends_list.itemClicked.connect(self.on_item_clicked)  # 连接点击事件

        # 右侧布局
        right_widget = QtWidgets.QWidget()  # 右侧的 widget
        right_layout = QtWidgets.QVBoxLayout(right_widget)

        # 当前聊天好友的名称
        self.current_friend_label = QtWidgets.QLabel("选择一个好友以开始聊天")
        self.current_friend_label.setAlignment(QtCore.Qt.AlignCenter)
        self.current_friend_label.setFont(QtGui.QFont("Arial", 14))
        right_layout.addWidget(self.current_friend_label)

        # 添加好友操作按钮
        self.friend_actions_layout = QtWidgets.QHBoxLayout()
        self.group_actions_layout = QtWidgets.QHBoxLayout()

        # 好友信息按钮
        self.friend_info_button = QtWidgets.QPushButton("好友信息")
        self.friend_info_button.clicked.connect(self.on_friend_info_button_click)  # 需要定义该方法
        self.friend_actions_layout.addWidget(self.friend_info_button, 1)

        # 在当前聊天好友的名称标签下添加发送文件按钮
        self.send_file_button = QtWidgets.QPushButton("发送文件")
        self.send_file_button.clicked.connect(self.on_send_file_button_click)  # 需要定义该方法
        self.friend_actions_layout.addWidget(self.send_file_button, 1)

        # 删除好友按钮
        self.delete_friend_button = QtWidgets.QPushButton("删除好友")
        self.delete_friend_button.clicked.connect(self.on_delete_friend_button_click)  # 需要定义该方法
        self.delete_friend_button.setStyleSheet("QPushButton { color: red; }")  # 设置文本颜色为红色
        self.friend_actions_layout.addWidget(self.delete_friend_button, 1)

        # 群聊信息按钮
        self.group_info_button = QtWidgets.QPushButton("群聊信息")
        self.group_info_button.clicked.connect(self.on_group_info_button_click)  # 需要定义该方法
        self.group_actions_layout.addWidget(self.group_info_button, 1)

        # 群聊信息按钮
        self.add_group_member_button = QtWidgets.QPushButton("邀请好友")
        self.add_group_member_button.clicked.connect(self.on_add_group_member_button_click)  # 需要定义该方法
        self.group_actions_layout.addWidget(self.add_group_member_button, 1)

        # 退出群聊按钮
        self.delete_group_button = QtWidgets.QPushButton("退出群聊")
        self.delete_group_button.clicked.connect(self.on_delete_group_button_click)  # 需要定义该方法
        self.delete_group_button.setStyleSheet("QPushButton { color: red; }")  # 设置文本颜色为红色
        self.group_actions_layout.addWidget(self.delete_group_button, 1)

        # 只有在选中好友时，按钮才可见
        self.friend_info_button.setVisible(False)
        self.delete_friend_button.setVisible(False)
        self.send_file_button.setVisible(False)

        self.group_info_button.setVisible(False)
        self.delete_group_button.setVisible(False)
        self.add_group_member_button.setVisible(False)

        right_layout.addLayout(self.friend_actions_layout)
        right_layout.addLayout(self.group_actions_layout)

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

        # 加载好友和群聊列表
        self.load_friends_and_groups()

    def auto_reload_friends_and_groups(self):
        while True:
            time.sleep(1)  # 每60秒刷新一次
            self.update_list_signal.emit()  # 通知主线程更新列表

    def display_group_add_member_list(self, group_info):
        group_id = self.current_item  # 当前选中的群聊 ID
        current_group_members = group_info['群聊成员']

        # 弹出添加群成员的对话框
        dialog = AddGroupMemberDialog(self.client.all_friends, current_group_members, parent=self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_friends = dialog.get_selected_friends()

            # 调用客户端的方法邀请好友到群聊
            for friend_name in selected_friends:
                friend_id = self.get_friend_id(friend_name)
                if friend_id is not None:
                    self.client.add_member_to_group(group_id, friend_id)

    def on_add_group_member_button_click(self):
        # 确保已选择群聊
        if self.current_chat_type != 'group' or self.current_item is None:
            QtWidgets.QMessageBox.warning(self, "操作错误", "请先选择一个群聊。")
            return

        group_id = self.current_item  # 当前选中的群聊 ID
        self.client.get_group_info_for_add_member(group_id)

    def on_delete_group_button_click(self):
        # 确保已选择群聊
        if self.current_chat_type != 'group' or self.current_item is None:
            QtWidgets.QMessageBox.warning(self, "操作错误", "请先选择一个群聊。")
            return

        group_id = self.current_item  # 当前选中的群聊 ID
        reply = QtWidgets.QMessageBox.question(
            self, '确认退出', '你确定要退出这个群聊吗？',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            # 发送退出群聊请求
            self.client.leave_group(group_id)

        self.group_info_button.setVisible(False)
        self.delete_group_button.setVisible(False)
        self.add_group_member_button.setVisible(False)

        thread = threading.Thread(target=self.reload_friends_and_groups_in_one_second())
        thread.start()

    def always_reload_friends_and_groups(self):
        while True:
            self.reload_friends_and_groups_in_one_second()

    def reload_friends_and_groups_in_one_second(self):
        time.sleep(1)
        self.load_friends_and_groups()  # 刷新好友列表

    def on_group_info_button_click(self):
        # 检查当前是否选择了群聊
        if self.current_chat_type == 'group' and self.current_item is not None:
            # 获取群聊信息
            self.client.get_group_info(self.current_item)
            # if group_info:
            #     # 创建对话框显示群聊信息
            #     dialog = QtWidgets.QDialog(self)
            #     dialog.setWindowTitle("群聊信息")
            #     layout = QtWidgets.QVBoxLayout(dialog)
            #
            #     # 显示群聊的各项信息
            #     for key, value in group_info.items():
            #         layout.addWidget(QtWidgets.QLabel(f"{key}: {value}"))
            #
            #     dialog.setLayout(layout)
            #     dialog.exec_()
            # else:
            #     QtWidgets.QMessageBox.warning(self, "错误", "无法获取群聊信息。")
        else:
            QtWidgets.QMessageBox.warning(self, "操作错误", "请先选择一个群聊。")

    def on_send_file_button_click(self):
        # TODO: 文件发送按钮
        pass

    def handle_friend_request_received(self, user_id, requester_id, requester_username):
        self.receive_friend_request(user_id, requester_id, requester_username)

    # 处理好友请求按钮点击事件
    def on_friend_request_button_click(self):
        self.client.check_friend_requests()

        self.load_friends_and_groups()  # 刷新好友列表

    # 处理添加好友按钮点击事件
    def on_add_friend_button_click(self):
        add_friend_dialog = AddFriendDialog(self)
        if add_friend_dialog.exec_() == QtWidgets.QDialog.Accepted:
            user_id_to_add = add_friend_dialog.get_user_id()
            self.client.send_add_friend_request(user_id_to_add)

    # 发起群聊按钮点击事件处理函数
    def on_create_group_button_click(self):
        dialog = CreateGroupDialog(self.client.all_friends, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_friends = dialog.get_selected_friends()
            group_name = dialog.get_group_name()  # 假设对话框提供获取群组名的方法
            self.client.create_group([f for f in selected_friends], group_name)

    def on_friend_info_button_click(self):
        # 显示选中的好友信息
        friend_id = self.current_item  # 当前选中的好友 ID
        if friend_id is not None:
            # 在主线程中执行操作，不需要开启新线程
            friend_info = self.client.get_friend_info(friend_id)
            self.show_friend_info(friend_info)
        else:
            QtWidgets.QMessageBox.warning(self, "提示", "请先选择一个好友")

    @QtCore.pyqtSlot(dict)
    def show_group_info(self, group_info: dict):
        # 如果已经存在一个信息对话框，先关闭它
        if self.info_dialog is not None:
            self.info_dialog.close()
            self.info_dialog = None

        if group_info:
            # 创建对话框显示群聊信息
            self.info_dialog = QtWidgets.QDialog(self)
            self.info_dialog.setWindowTitle("群聊信息")
            self.info_dialog.setWindowModality(QtCore.Qt.NonModal)  # 设置为非模态

            # 设置对话框大小
            self.info_dialog.resize(400, 200)  # 设置为400x300的大小

            # 设置对话框布局
            layout = QtWidgets.QVBoxLayout()

            # 显示群聊的各项信息
            for key, value in group_info.items():
                layout.addWidget(QtWidgets.QLabel(f"{key}: {value}"))

            self.info_dialog.setLayout(layout)
            self.info_dialog.finished.connect(self.on_info_dialog_closed)  # 连接对话框关闭信号
            self.info_dialog.show()  # 非模态显示对话框

    # 将 show_friend_info 调整为接收信号
    @QtCore.pyqtSlot(dict)
    def show_friend_info(self, friend_info):
        # 如果已经存在一个信息对话框，先关闭它
        if self.info_dialog is not None:
            self.info_dialog.close()
            self.info_dialog = None

        if friend_info:
            # 创建一个新的对话框来显示好友信息
            self.info_dialog = QtWidgets.QDialog(self)
            self.info_dialog.setWindowTitle("好友信息")
            self.info_dialog.setWindowModality(QtCore.Qt.NonModal)  # 设置为非模态

            # 设置对话框大小
            self.info_dialog.resize(400, 200)  # 设置为400x300的大小

            # 设置对话框布局
            layout = QtWidgets.QVBoxLayout()

            # 假设 friend_info 是一个包含各种信息的字典
            for key, value in friend_info.items():
                layout.addWidget(QtWidgets.QLabel(f"{key}: {value}"))

            self.info_dialog.setLayout(layout)
            self.info_dialog.finished.connect(self.on_info_dialog_closed)  # 连接对话框关闭信号
            self.info_dialog.show()  # 非模态显示对话框
        else:
            QtWidgets.QMessageBox.warning(self, "错误", "无法获取好友信息。")

    def on_delete_friend_button_click(self):
        friend_id = self.current_item  # 当前选中的好友 ID
        if friend_id is not None:
            reply = QtWidgets.QMessageBox.question(
                self, '确认删除', '你确定要删除这位好友吗？',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

            if reply == QtWidgets.QMessageBox.Yes:
                if self.client.delete_friend(friend_id):
                    QtWidgets.QMessageBox.information(self, "删除成功", "好友已经被成功删除。")
                    self.load_friends_and_groups()  # 刷新好友列表

                    self.friend_info_button.setVisible(False)
                    self.delete_friend_button.setVisible(False)
                    self.send_file_button.setVisible(False)
                else:
                    QtWidgets.QMessageBox.warning(self, "删除失败", "无法删除该好友。")
        else:
            QtWidgets.QMessageBox.warning(self, "操作错误", "请先选择一个好友。")

    def on_info_dialog_closed(self):
        # 对话框关闭时的处理
        self.info_dialog = None  # 将对话框引用设置为 None

    def load_friends_and_groups(self):
        # 清空当前的好友和群组列表
        self.friends_list.clear()

        # 重新从客户端加载好友和群组
        self.client.all_friends = self.client.get_friend_list()
        self.client.all_groups = self.client.get_group_list()

        # 添加好友和群组到列表
        for friend in self.client.all_friends:
            self.add_list_item(friend, is_friend=True)
        for group in self.client.all_groups:
            self.add_list_item(group, is_friend=False)

        # 更新当前选中的项目或清除消息区域等
        self.current_item = None
        if hasattr(self, 'messages_area'):
            self.messages_area.clear()
        if hasattr(self, 'current_friend_label'):
            self.current_friend_label.setText("选择一个好友以开始聊天")

        self.friend_info_button.setVisible(False)
        self.delete_friend_button.setVisible(False)
        self.send_file_button.setVisible(False)

        self.group_info_button.setVisible(False)
        self.delete_group_button.setVisible(False)
        self.add_group_member_button.setVisible(False)

    def add_list_item(self, item, is_friend):
        if is_friend:
            friend_id, friend_name = item[0], item[1]
            latest_message, sender_id = self.client.database.get_latest_message_with_sender(self.client.user_id,
                                                                                            friend_id)
            if latest_message and sender_id:
                prefix = "你:" if int(sender_id) == self.client.user_id else "对方:"
                latest_message = f"{prefix}{latest_message[:5]}..." if len(
                    latest_message) > 5 else f"{prefix}{latest_message}"
            label_text = friend_name
            name_object_name = f"name_label_{friend_id}"
            message_object_name = f"message_label_{friend_id}"
        else:
            group_id, group_name = item[0], item[1]
            latest_message, sender_name = self.client.database.get_latest_group_message_with_sender(group_id)

            if latest_message and sender_name:
                sender_prefix = '你' if self.client.username == sender_name else sender_name
                latest_message = f"{sender_prefix}: {latest_message[:5]}..." if len(
                    latest_message) > 5 else f"{sender_prefix}: {latest_message}"
            label_text = group_name
            name_object_name = f"group_label_{group_id}"
            message_object_name = f"group_message_label_{group_id}"

        # 创建自定义列表项
        item_widget = QtWidgets.QWidget()
        item_layout = QtWidgets.QVBoxLayout(item_widget)

        # 名称加粗放大显示
        name_label = QtWidgets.QLabel(label_text)
        name_label.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        name_label.setObjectName(name_object_name)  # 设置好友名称标签的对象名称
        item_layout.addWidget(name_label)

        # 最近一条聊天记录小字显示
        message_label = QtWidgets.QLabel(latest_message)
        message_label.setFont(QtGui.QFont("Arial", 10))
        message_label.setObjectName(message_object_name)  # 设置消息预览标签的对象名称
        item_layout.addWidget(message_label)

        # 创建列表项，将自定义 widget 作为其子项
        list_item = QtWidgets.QListWidgetItem(self.friends_list)
        list_item.setSizeHint(item_widget.sizeHint())  # 设置列表项的大小

        # 添加列表项到列表中
        self.friends_list.addItem(list_item)
        self.friends_list.setItemWidget(list_item, item_widget)

    def on_item_clicked(self, item):
        item_widget = self.friends_list.itemWidget(item)
        label = item_widget.findChild(QtWidgets.QLabel)
        if label.objectName().startswith("name_label_"):
            self.handle_friend_click(label.text())
        elif label.objectName().startswith("group_label_"):
            self.handle_group_click(label.text())

    def handle_group_click(self, group_name):
        group_id = self.get_group_id(group_name)
        if group_id is None:
            return

        self.current_item = group_id
        self.current_chat_type = 'group'

        self.current_friend_label.setText(f"{group_name}")
        self.messages_area.clear()

        # 加载与该群组的聊天记录
        group_messages = self.client.database.get_group_messages(group_id)
        for content, sender_id, timestamp in group_messages:
            self.display_group_message_from_database(group_id, sender_id, content, timestamp)

        if not self.client.connected:
            self.display_error_message('[OFF-LINE] Another user logged in with your user ID. You have '
                                       'been disconnected.')

        self.friend_info_button.setVisible(False)
        self.delete_friend_button.setVisible(False)
        self.send_file_button.setVisible(False)

        self.group_info_button.setVisible(True)
        self.delete_group_button.setVisible(True)
        self.add_group_member_button.setVisible(True)


    def get_group_id(self, group_name):
        for group in self.client.all_groups:
            if group[1] == group_name:
                return group[0]
        return None

    def handle_friend_click(self, friend_name):
        friend_id = self.get_friend_id(friend_name)
        if friend_id is None:
            return

        self.current_item = friend_id
        self.current_chat_type = 'friend'

        self.current_friend_label.setText(friend_name)
        self.messages_area.clear()

        # 加载与该好友的聊天记录
        chat_messages = self.client.database.get_chat_messages(self.client.user_id, friend_id)
        for content, sender_id, timestamp in chat_messages:
            self.display_message_from_database(sender_id, content, timestamp)

        if not self.client.connected:
            self.display_error_message('[OFF-LINE] Another user logged in with your user ID. You have '
                                       'been disconnected.')

        self.friend_info_button.setVisible(True)
        self.delete_friend_button.setVisible(True)
        self.send_file_button.setVisible(True)

        self.group_info_button.setVisible(False)
        self.delete_group_button.setVisible(False)
        self.add_group_member_button.setVisible(False)

    def get_friend_id(self, friend_name):
        for friend in self.client.all_friends:
            if friend[1] == friend_name:
                return friend[0]
        return None

    def display_error_message(self, message):
        formatted_message = f"<b><font color='red'>{message}</font></b>"

        self.messages_area.append(formatted_message)
        self.messages_area.append(formatted_message)
        self.messages_area.append(formatted_message)

        self.messages_area.ensureCursorVisible()  # 确保光标可见
        self.scroll_to_bottom()  # 然后滚动到底部

    # display_message 函数用于显示实时收到的消息
    def display_message(self, sender_id, message, timestamp):
        # 获取消息发送者的用户名，如果是当前用户，则显示 "你"

        chat_id = self.current_item if self.current_chat_type == 'friend' else sender_id
        last_time = self.get_last_message_time(chat_id)
        if self.should_display_time(timestamp, last_time):
            self.messages_area.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

        self.messages_area.append(message)
        self.messages_area.ensureCursorVisible()  # 确保光标可见
        self.scroll_to_bottom()  # 然后滚动到底部
        self.update_last_message_time(chat_id, timestamp)

    # display_message_from_database 函数用于显示从数据库中加载的消息
    def display_message_from_database(self, sender_id, message, timestamp_str):
        # 获取消息发送者的用户名，如果是当前用户，则显示 "你"
        sender_name = "你" if sender_id == self.client.user_id else self.client.get_friend_name(sender_id)
        formatted_message = f"{sender_name}: {message}"

        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone('Asia/Shanghai'))

        # 检查是否需要显示时间
        if self.should_display_time(timestamp, self.last_message_time):
            self.messages_area.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

        self.messages_area.append(formatted_message)
        self.messages_area.ensureCursorVisible()  # 确保光标可见
        self.scroll_to_bottom()  # 然后滚动到底部
        self.last_message_time = timestamp  # 更新上一条消息的时间戳

    # display_group_message 函数用于显示实时收到的群聊消息
    def display_group_message(self, group_id, sender_id, message, timestamp):
        # 获取消息发送者的用户名，如果是当前用户，则显示 "你"
        sender_name = "你" if sender_id == self.client.user_id else self.client.get_friend_name(sender_id)

        formatted_message = f"{sender_name}: {message}"

        chat_id = self.current_item if self.current_chat_type == 'friend' else sender_id
        last_time = self.get_last_message_time(chat_id)
        if self.should_display_time(timestamp, last_time):
            self.messages_area.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

        self.messages_area.append(formatted_message)
        self.messages_area.ensureCursorVisible()  # 确保光标可见
        self.scroll_to_bottom()  # 然后滚动到底部

        self.last_message_time = timestamp

    # display_group_message 函数用于显示实时收到的群聊消息
    def display_current_group_message(self, group_id, sender_id, message, timestamp):
        # 获取消息发送者的用户名，如果是当前用户，则显示 "你"
        sender_name = "你" if sender_id == self.client.user_id else self.client.get_friend_name(sender_id)
        group_name = self.client.get_group_name(group_id)

        formatted_message = f"<b>{group_name}@{sender_name}: {message}</b>"

        chat_id = self.current_item if self.current_chat_type == 'friend' else sender_id
        last_time = self.get_last_message_time(chat_id)
        if self.should_display_time(timestamp, last_time):
            self.messages_area.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

        self.messages_area.append(formatted_message)
        self.messages_area.ensureCursorVisible()  # 确保光标可见
        self.scroll_to_bottom()  # 然后滚动到底部
        self.last_message_time = timestamp

    # display_group_message_from_database 函数用于显示从数据库中加载的群聊消息
    def display_group_message_from_database(self, group_id, sender_id, message, timestamp_str):
        # 获取消息发送者的用户名，如果是当前用户，则显示 "你"
        sender_name = "你" if sender_id == self.client.user_id else self.client.get_friend_name(sender_id)
        formatted_message = f"{sender_name}: {message}"

        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone('Asia/Shanghai'))

        # 检查是否需要显示时间
        if self.should_display_time(timestamp, self.last_message_time):
            self.messages_area.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

        self.messages_area.append(formatted_message)
        self.messages_area.ensureCursorVisible()  # 确保光标可见
        self.scroll_to_bottom()  # 然后滚动到底部

        self.last_message_time = timestamp  # 更新上一条消息的时间戳

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.on_send_button_click()

    def display_message_normal(self, message, timestamp):
        # 获取当前聊天好友的最后一条消息时间戳
        last_time = self.last_message_time_per_chat.get(self.current_item)

        # 检查是否需要显示时间
        if self.should_display_time(timestamp, last_time):
            self.messages_area.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

        self.messages_area.append(message)
        self.messages_area.ensureCursorVisible()  # 确保光标可见
        self.scroll_to_bottom()  # 然后滚动到底部

        self.last_message_time_per_chat[self.current_item] = timestamp  # 更新当前聊天好友的最后消息时间戳

    def on_send_button_click(self):
        # 如果没有选择好友或群组，不执行发送操作
        if self.current_item is None:
            QtWidgets.QMessageBox.warning(self, "提示", "请先选择一个好友或群组")
            return

        message = self.message_entry.text().strip()
        # 确保消息非空
        if not message:
            return

        # 发送消息并更新列表
        if self.current_chat_type == 'friend':
            self.client.send_message(self.current_item, message)
            self.update_list_item_message_preview(self.current_item, message, True)
        elif self.current_chat_type == 'group':
            self.client.send_message(self.current_item, message, is_group=True)
            self.update_list_item_message_preview(self.current_item, message, True, is_group=True)

        # 获取当前时间，并转换为时区感知的 datetime 对象
        current_datetime = datetime.now(pytz.timezone('Asia/Shanghai'))
        self.display_message_normal(f"你: {message}", current_datetime)

        # 清空消息输入框
        self.message_entry.clear()

    def update_list_item_message_preview(self, chat_id, message, is_sender, is_group=False):
        for index in range(self.friends_list.count()):
            item = self.friends_list.item(index)
            widget = self.friends_list.itemWidget(item)

            label_name = f"group_message_label_{chat_id}" if is_group else f"message_label_{chat_id}"
            message_label = widget.findChild(QtWidgets.QLabel, label_name)

            if message_label:
                short_message = (message[:5] + '...') if len(message) > 5 else message
                prefix = "你:"
                message_label.setText(f"{prefix}{short_message}")
                break

    def update_list_item_message_preview_when_receive(self, chat_id, message, sender_name, is_group=False):
        for index in range(self.friends_list.count()):
            item = self.friends_list.item(index)
            widget = self.friends_list.itemWidget(item)

            label_name = f"group_message_label_{chat_id}" if is_group else f"message_label_{chat_id}"
            message_label = widget.findChild(QtWidgets.QLabel, label_name)

            if message_label:
                short_message = (message[:5] + '...') if len(message) > 5 else message
                prefix = f'{sender_name}:'
                message_label.setText(f"{prefix}{short_message}")
                break

    def on_friend_clicked(self, item):
        # 获取当前点击的列表项对应的自定义 widget
        item_widget = self.friends_list.itemWidget(item)
        # 通过 item_widget 中的子 widget（如 QLabel）获取数据
        friend_name = item_widget.findChild(QtWidgets.QLabel).text()
        friend_id = self.get_friend_id(friend_name)  # 假设这个方法能够根据好友名获取其 user_id
        self.current_item = friend_id
        self.current_friend_label.setText(f"{friend_name}")
        self.messages_area.clear()

        # 获取当前好友的最后消息时间戳
        last_time = self.last_message_time_per_chat.get(friend_id)

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
        self.last_message_time_per_chat[friend_id] = last_time

    def scroll_to_bottom(self):
        # 处理所有挂起的事件，确保文本编辑区域已更新
        QApplication.processEvents()
        # 然后滚动到底部
        self.messages_area.verticalScrollBar().setValue(
            self.messages_area.verticalScrollBar().maximum())

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

    # 更新最后消息时间的函数
    def update_last_message_time(self, chat_id, timestamp):
        self.last_message_time_per_chat[chat_id] = timestamp

    # 获取最后消息时间的函数
    def get_last_message_time(self, chat_id):
        return self.last_message_time_per_chat.get(chat_id)

    def run(self):
        self.show()

    def receive_friend_request(self, user_id, requester_id, requester_username):
        # 创建一个对话框来显示请求信息，并提供接受和拒绝按钮
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setWindowTitle("好友请求")
        msg_box.setText(f"用户 {requester_username} 想要添加您为好友。")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        # # 连接按钮的信号与相应的槽
        # result = msg_box.exec_()
        # if result == QtWidgets.QMessageBox.Yes:
        #     self.respond_to_friend_request(requester_id, True)
        # elif result == QtWidgets.QMessageBox.No:
        #     self.respond_to_friend_request(requester_id, False)
        result = msg_box.exec_()
        self.respond_to_friend_request(requester_id, result == QtWidgets.QMessageBox.Yes)

    def respond_to_friend_request(self, requester_id, accept):
        if accept:
            self.client.accept_friend_request(requester_id)
        else:
            self.client.reject_friend_request(requester_id)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    client = Client()  # 应传入实际的 Client 对象
    gui = GUI(client)
    gui.run()
    sys.exit(app.exec_())
