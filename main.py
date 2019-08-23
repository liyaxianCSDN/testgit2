# -*- coding:utf-8 -*-

import sys
from test_cases import *          # 有用
from settings import CASES_DICT
from api.api import API
from common import *
import logging
import traceback


logger = logging.getLogger()


if __name__ == '__main__':
    # arg = sys.argv[1]               # 获取命令行参数，得到字符串类型测试输入
    # str_input = arg.replace(';', ',')      # 将字符串中的;替换为,
    # d_input = eval(str_input)                    # 将字符串转为python字典

    # 以下为测试数据
    d_input = dict()
    d_input['instance_count'] = 1
    d_input['instance_names'] = ['instance_name1']
    d_input['instance_ips'] = ['127.0.0.1']
    d_input['instance_backupips'] = ['172.16.3.80']
    d_input['instance_redundancy_ips'] = ['172.16.3.81']
    d_input['instance_redundancy_backupips'] = ['172.16.3.82']
    d_input['case_id'] = 'ASyncGetHistoryDataObjectRecordSets_1'
    d_input['check'] = '暂时没想到咋校验'
    d_input['obj_names'] = ['obj_name']
    d_input['data_versions'] = [1]
    d_input['start_times'] = ['2019-08-06 13:57:32.265']
    d_input['end_times'] = ['2019-08-06 13:57:42.265']
    d_input['time_realtions'] = [14]
    # 以上为测试数据

    api = API(d_input)
    res = wait(600, api.connect)  # 10分钟连不上不再重连
    if res.get('result_code') != 1:  # 连接服务失败，跳过用例
        result = dict(
            case_id=d_input.get('case_id'),
            date=now(),
            status='未结束',
            exec_point='connect',
            result_code=res.get('result_code'),
        )
    else:
        func_name = d_input.get('case_id').split('_')[0]
        func = CASES_DICT.get(func_name)            # 根据case_id获取对应的用例执行函数
        case_id = d_input.get('case_id')
        if not func or not callable(func):            # badcase 过滤错误的case_id
            result = dict(
                case_id=case_id,
                date=now(),
                status='未执行',
                exec_point='match_cases',
                result_code=-1,
            )
        logger.critical('Run Test: %s' % case_id)
        try:
            result = func(d_input)                      # 执行用例
        except:
            result = dict(
                case_id=case_id,
                date=now(),
                status='未知异常，查看日志',
                exec_point='exec_cases',
                result_code=-1,
            )
            logger.error(traceback.format_exc())        # 输出用例执行异常追踪信息
    logger.critical(str(result))





