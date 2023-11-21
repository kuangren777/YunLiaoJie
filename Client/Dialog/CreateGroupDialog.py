# -*- coding: utf-8 -*-
# @Time    : 2023/11/21 19:18
# @Author  : KuangRen777
# @File    : CreateGroupDialog.py
# @Tags    :
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication
import pytz


class CreateGroupDialog(QtWidgets.QDialog):
    def __init__(self, friends_list, parent=None):
        super(CreateGroupDialog, self).__init__(parent)
        self.setWindowTitle('发起群聊')
        self.layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel("选择要添加到群聊的朋友:")
        self.layout.addWidget(self.label)

        self.friends_list_widget = QtWidgets.QListWidget(self)
        for friend in friends_list:
            item = QtWidgets.QListWidgetItem(friend[1])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
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
            if item.checkState() == QtCore.Qt.Checked:
                selected_friends.append(item.text())
        return selected_friends
