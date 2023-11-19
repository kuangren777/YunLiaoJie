# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 15:34
# @Author  : KuangRen777
# @File    : login_gui.py
# @Tags    :
import sys
from Server.authentication import Authentication
from Server.database import Database

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QDialog
from PyQt5.QtGui import QFont  # 导入字体类
from Client.gui import GUI


class LoginWindow(QDialog):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.user_info = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("登录")
        layout = QVBoxLayout()

        # 创建标题 QLabel
        title_label = QLabel("云聊界登录系统", self)
        title_label.setAlignment(QtCore.Qt.AlignCenter)  # 上下居中
        title_label.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))  # 设置字体为粗体
        layout.addWidget(title_label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_button = QPushButton("登录", self)
        login_button.clicked.connect(self.on_login_clicked)
        layout.addWidget(login_button)

        self.register_button = QPushButton("注册新账号", self)
        self.register_button.clicked.connect(self.on_register_clicked)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        # 固定窗口大小为300x200像素
        self.setFixedSize(300, 200)

    def on_login_clicked(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.user_info = self.auth.login_user(username, password)
        if self.user_info:
            QMessageBox.information(self, "登录成功", "登录成功！")
            self.accept()  # 关闭窗口，并返回 QDialog.Accepted
        else:
            QMessageBox.warning(self, "登录失败", "用户名或密码错误！")
            self.reject()  # 关闭窗口，并返回 QDialog.Rejected

    def on_register_clicked(self):
        self.hide()
        self.register_window = RegisterWindow(self.auth)
        self.register_window.show()

    # def open_main_window(self, user_info):
    #     self.hide()
    #     # 假设您的主界面 GUI 类需要用户信息作为参数
    #     self.main_window = GUI(user_info)  # 创建主界面窗口实例
    #     self.main_window.run()


class RegisterWindow(QWidget):
    def __init__(self, auth):
        super().__init__()
        self.auth = auth
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("注册")
        layout = QVBoxLayout()

        # 创建标题 QLabel
        title_label = QLabel("云聊界登录系统", self)
        title_label.setAlignment(QtCore.Qt.AlignCenter)  # 上下居中
        title_label.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))  # 设置字体为粗体
        layout.addWidget(title_label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("邮箱")
        layout.addWidget(self.email_input)

        register_button = QPushButton("注册", self)
        register_button.clicked.connect(self.on_register_clicked)
        layout.addWidget(register_button)

        self.login_button = QPushButton("返回登录", self)
        self.login_button.clicked.connect(self.on_login_clicked)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        # 固定窗口大小为300x200像素
        self.setFixedSize(300, 300)

    def on_register_clicked(self):
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        if self.auth.register_user(username, password, email):
            QMessageBox.information(self, "注册成功", "注册成功！")
            self.hide()
            self.login_window = LoginWindow(self.auth)
            self.login_window.show()
        else:
            QMessageBox.warning(self, "注册失败", "注册失败，请重试！")

    def on_login_clicked(self):
        self.hide()
        self.login_window = LoginWindow(self.auth)
        self.login_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 这里假设您已经创建了 Authentication 实例
    db = Database()  # 假设数据库实例化
    auth = Authentication(db)

    login_window = LoginWindow(auth)
    login_window.show()

    sys.exit(app.exec_())
