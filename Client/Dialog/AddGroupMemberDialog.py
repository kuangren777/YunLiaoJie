# -*- coding: utf-8 -*-
# @Time    : 2023/11/27 22:46
# @Author  : KuangRen777
# @File    : AddGroupMemberDialog.py
# @Tags    :
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication
import pytz


class AddGroupMemberDialog(QtWidgets.QDialog):
    def __init__(self, friends_list, current_group_members, parent=None):
        super(AddGroupMemberDialog, self).__init__(parent)
        print(f'current_group_members:{current_group_members}')
        self.setWindowTitle('邀请好友')
        self.layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel("选择要添加到群聊的朋友:")
        self.layout.addWidget(self.label)

        self.friends_list_widget = QtWidgets.QListWidget(self)
        for friend in friends_list:
            friend_id, friend_name = friend[0], friend[1]
            item = QtWidgets.QListWidgetItem(friend_name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)

            print(f'current_group_members:{current_group_members}')

            # 如果当前好友已经是群聊成员，则默认勾选并禁用选择
            if friend_name in current_group_members:
                item.setCheckState(QtCore.Qt.Checked)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

            self.friends_list_widget.addItem(item)

        self.layout.addWidget(self.friends_list_widget)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def get_selected_friends(self):
        selected_friends = []
        for index in range(self.friends_list_widget.count()):
            item = self.friends_list_widget.item(index)
            if item.checkState() == QtCore.Qt.Checked and item.flags() & QtCore.Qt.ItemIsEnabled:
                selected_friends.append(item.text())
        return selected_friends
