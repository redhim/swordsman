# -*- coding: utf-8 -*-
'''
日志模块
'''
import logging
from logging.handlers import RotatingFileHandler


def log_init():
    logger = logging.getLogger()
    info_level = logging.INFO
    logger.setLevel(level=info_level)
    # 定义一个RotatingFileHandler，最多备份10个日志文件，每个日志文件最大5M
    rHandler = RotatingFileHandler("../log/log.txt", maxBytes=5 * 1024 * 1024, backupCount=10)
    rHandler.setLevel(level=info_level)
    formatter = logging.Formatter('%(asctime)s - %(filename)s -%(funcName)s- %(levelname)s - %(message)s')
    rHandler.setFormatter(formatter)
    # 输出到控制台设置
    console = logging.StreamHandler()
    console.setLevel(info_level)
    console.setFormatter(formatter)
    logger.addHandler(rHandler)
    logger.addHandler(console)
    return logger


# 日志对象
logger = log_init()
