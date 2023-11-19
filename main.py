# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:21
# @Author  : KuangRen777
# @File    : main.py
# @Tags    :
import sys
from server.server import Server
from client.client import Client
import config

# conda activate yunliaojie
# cd C:\Users\luomi\PycharmProjects\YunLiaoJie
# python main.py client
# python main.py server


def main():
    if len(sys.argv) < 2:
        print("Usage: main.py <server/client>")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == 'server':
        server = Server(config.SERVER_HOST, config.SERVER_PORT)
        server.start()
    elif mode == 'client':
        client = Client(config.SERVER_HOST, config.SERVER_PORT)
        client.start()
    else:
        print("Invalid mode. Use 'server' or 'client'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
