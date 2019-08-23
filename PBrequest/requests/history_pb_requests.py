# -*- coding:utf-8 -*-
'''
各子系统需要实现针对自己系统的pb请求构造函数
该文件为历史库pb请求构造函数文件的实现样例
各子系统可自定义文件名，放入与该文件相同路径下即可
引用关系可参考该文件
'''

from datetime import datetime
from PBrequest.pb.history_pb2 import GetHistoryDataObjectRecordSetsRequest
import logging


logger = logging.getLogger()


def get_history_data_object_record_set_request(default={}):     # pb格式的message GetHistoryDataObjectRecordSetsRequest构造函数
    # 构造历史数据查询请求对象
    logger.info('start make pb_request.')
    pb_request = GetHistoryDataObjectRecordSetsRequest()
    obj_names = default.get('obj_names')
    data_versions = default.get('data_versions')
    start_times = default.get('start_times')
    end_times = default.get('end_times')
    time_relations = default.get('time_realtions')
    pb_request.history_data_object_names.extend(obj_names)
    pb_request.data_versions.extend(data_versions)
    for st, et in zip(start_times, end_times):
        time_scope = pb_request.time_scopes.add()
        try:
            st = datetime.strptime(st, '%Y-%m-%d %H:%M:%S.%f')
            et = datetime.strptime(et, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            st = datetime.strptime(st, '%Y-%m-%d %H:%M:%S')
            et = datetime.strptime(et, '%Y-%m-%d %H:%M:%S')
        time_scope.start_time.FromDatetime(st)   # 这里没有进行时区转换，使用时注意是否需要转换时区
        time_scope.end_time.FromDatetime(et)
    if time_relations:  # 注意检验未输入参数，这里只是用time_relations举个例子
        pb_request.time_relations.extend(time_relations)
    byte_data = pb_request.SerializeToString()
    byte_size = pb_request.ByteSize()
    res = dict(request_name=pb_request.__class__.__name__, size=byte_size, data=byte_data)      # 构造函数需遵循此统一的返回值格式
    return res


def get_history_data_object_record_sets_by_time_position_request(default={}):
    print('test')
    # pass


def subscribe_history_data_object_record_sets(default={}):
    pass


def add_history_data_object_record_sets(default={}):
    pass


# 以下内容为测试用，可忽略
if __name__ == '__main__':
    pb_request = GetHistoryDataObjectRecordSetsRequest()
    obj_names = ['1']
    pb_request.history_data_object_names.extend(obj_names)
    pb_request.time_relations.extend([1, 2, 5, 6])
    print(type(pb_request))
    print(dir(pb_request.history_data_object_names))
    print(pb_request.history_data_object_names)
    # print(len(pb_request.history_data_object_names))




















