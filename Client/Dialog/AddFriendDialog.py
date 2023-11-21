# -*- coding: utf-8 -*-
# @Time    : 2023/11/21 19:16
# @Author  : KuangRen777
# @File    : AddFriendDialog.py
# @Tags    :
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication
import pytz


class AddFriendDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('添加好友')
        self.layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel("请输入好友的 User ID:")
        self.layout.addWidget(self.label)

        self.friend_id_input = QtWidgets.QLineEdit(self)
        self.layout.addWidget(self.friend_id_input)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)

    def get_user_id(self):
        return self.friend_id_input.text().strip()
