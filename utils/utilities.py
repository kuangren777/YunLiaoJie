# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:25
# @Author  : KuangRen777
# @File    : utilities.py
# @Tags    :
import uuid
import datetime


def generate_unique_id():
    """
    生成唯一的标识符。
    """
    return str(uuid.uuid4())


def current_timestamp():
    """
    获取当前时间戳。
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_message(sender, message):
    """
    格式化聊天消息。
    """
    timestamp = current_timestamp()
    return f"[{timestamp}] {sender}: {message}"


# 示例用法
if __name__ == "__main__":
    unique_id = generate_unique_id()
    print("Unique ID:", unique_id)

    formatted_message = format_message("Alice", "Hello, Bob!")
    print("Formatted Message:", formatted_message)
