# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:24
# @Author  : KuangRen777
# @File    : encryption.py
# @Tags    :
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken



class Encryption:
    def __init__(self, key=None):
        self.key = key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        encrypted_data = self.cipher_suite.encrypt(data)
        return encrypted_data

    def decrypt(self, encrypted_data):
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return decrypted_data
        except InvalidToken:
            # 处理无效令牌异常，可以记录错误并返回适当的值
            print("Invalid token or data corrupted.")
            return None  # 或者返回其他适当的默认值或错误信息


# 示例用法
if __name__ == "__main__":
    encryption = Encryption()

    original_message = "Hello, this is a test message."
    encrypted_message = encryption.encrypt(original_message)
    print("Encrypted:", encrypted_message)

    decrypted_message = encryption.decrypt(encrypted_message)
    print("Decrypted:", decrypted_message)
