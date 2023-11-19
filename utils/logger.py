# -*- coding: utf-8 -*-
# @Time    : 2023/11/19 10:24
# @Author  : KuangRen777
# @File    : logger.py
# @Tags    :
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name, log_file, level=logging.INFO):
    """
    配置并获取一个日志记录器。
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 创建一个文件处理器，用于写入日志文件
    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
    handler.setFormatter(formatter)

    # 获取一个日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


# 示例用法
if __name__ == "__main__":
    logger = setup_logger('example_logger', 'example.log')
    logger.info("This is an info message")
    logger.error("This is an error message")
