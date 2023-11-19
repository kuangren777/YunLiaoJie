# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:23
# @Author  : KuangRen777
# @File    : chat.py
# @Tags    :
from client.messaging import Chat  # 导入 Chat 类
from client.messaging import Client  # 导入 Client 类

# 测试代码，实际使用时应在 client.py 中初始化和管理 ChatSession 实例
if __name__ == "__main__":
    client = Client("127.0.0.1", 8000)  # 创建一个Client实例
    chat_session = Chat(client)  # 将Client实例传递给Chat
    chat_session.set_current_chat("friend_id")
    chat_session.send_message("你好！")
