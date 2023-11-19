# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : gui.py
# @Tags    :
import tkinter as tk
from tkinter import scrolledtext


class GUI:
    def __init__(self, client):
        self.client = client
        self.window = tk.Tk()
        self.window.title("云聊界客户端")

        self.setup_ui()

    def setup_ui(self):
        # 创建消息显示区域
        self.messages_area = scrolledtext.ScrolledText(self.window, state='disabled', height=15)
        self.messages_area.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

        # 创建消息输入框
        self.message_entry = tk.Entry(self.window, width=50)
        self.message_entry.grid(row=1, column=0, sticky='nsew', padx=5)

        # 创建发送按钮
        self.send_button = tk.Button(self.window, text="发送", command=self.on_send_button_click)
        self.send_button.grid(row=1, column=1, sticky='nsew', padx=5)

        # 配置窗口网格行列权重，使窗口大小调整时元素表现正常
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

    def display_message(self, message):
        self.messages_area.config(state='normal')
        self.messages_area.insert(tk.END, message + '\n')
        self.messages_area.config(state='disabled')
        self.messages_area.yview(tk.END)

    def on_send_button_click(self):
        message = self.message_entry.get()
        self.client.send_message(message)
        self.message_entry.delete(0, tk.END)

    def run(self):
        self.window.mainloop()


# 这里只是为了测试 GUI，实际上应该在 client.py 中创建和运行 GUI
if __name__ == "__main__":
    gui = GUI(None)  # 正常情况下应该传入一个 Client 对象
    gui.run()
