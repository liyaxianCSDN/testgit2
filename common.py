# -*- coding:utf-8 -*-

'''
该文件封装了测试逻辑开发时需要用到的通用的函数，如获取当前日期时间、等待函数等
'''

from datetime import datetime
import time
import logging


logger = logging.getLogger()


def now():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')


def wait(seconds, func, *args):
    st = time.time()
    now = time.time()
    res = {'result_code': 0}
    while now - st < seconds:
        res = func(*args)
        if res['result_code'] == 1:    # 假设返回1为执行成功
            return res
        time.sleep(3)
        now = time.time()
    logger.warning('func_name: %s timeout(%d)s' % (func.__name__, seconds))
    return res

