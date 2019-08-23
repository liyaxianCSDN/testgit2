# -*- coding:utf-8 -*-

import yaml
import os
import logging.config

CASES_DICT = dict()     # 定义全局字典，存储test_cases中实现的所有测试函数


def load_config():          # 加载日志配置文件
    path = os.path.join(os.path.dirname(__file__), 'logging.yml')
    with open(path, 'r') as f_conf:
        d_conf = yaml.full_load(f_conf)
    file_handler = d_conf.get('handlers').get('file')
    if file_handler:
        file_path = file_handler.setdefault('filename', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log/frame.log'))
        base_path = os.path.dirname(file_path)
        try:
            os.makedirs(base_path)
        except FileExistsError:
            pass
    logging.config.dictConfig(d_conf)


try:
    load_config()
except Exception as e:
    print('加载配置文件失败')
    raise e

