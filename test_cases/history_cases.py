# -*- coding:utf-8 -*-

'''
各子系统需要实现针对自己系统的测试用例执行函数，封装适合自己系统的测试执行逻辑
该文件为历史库几个接口的测试执行逻辑实现样例
各子系统可自定义文件名，放入与该文件相同路径下即可
引用关系可参考该文件
'''

from settings import CASES_DICT
from PBrequest.requests import history_pb_requests
from PBrequest.pb import history_pb2
from api.api import API
from common import *
import time
import logging
import traceback

logger = logging.getLogger()


def sync_get_history_data_object_record_sets(default={}):
    '''
    同步查询历史数据记录用例实现：
    
    创建API实例并初始化
    连接服务
    
    构造请求参数
    调用请求方法，发送同步请求
    返回结果或超时
    
    结果验证
    测试数据统计并输出
    测试结束
    '''

    case_id = default.get('case_id')
    date = now()
    check_case = default.get('check')      # 校验规则应该也是个字典
    check_result = '未校验'

    api = API(default)                     # 实例化API类

    request = history_pb_requests.get_history_data_object_record_set_request(default)       # 从自己实现的PB请求构造文件中获取对应接口的PB格式的请求
    res = api.sync_pb_blob_request_call(request)                # 同步接口请求调用
    result_code = res.get('result_code')
    totle_time = res.get('et', 0) - res.get('st', 0)            # 同步接口调用耗时统计
    if result_code == 1:                                        # 如果返回值为成功，执行结果校验逻辑；否则直接返回测试结果
        response = res.get('response')
        # pb_response = history_pb2.GetHistoryDataObjectRecordSetsResponse()
        pb_request = history_pb2.GetHistoryDataObjectRecordSetsRequest()       # 测试为了简单，重用了request作为响应，这里只是验证功能
        # pb_response.ParseFromString(response.responseBody.data)
        pb_request.ParseFromString(response.responseBody.data)

        # object_recordsets = pb_response.object_recordsets
        # data_count = len(object_recordsets)  # 伪代码,不一定这么写，看具体对象结构
        data_count = len(pb_request.history_data_object_names)
        # 验证object_recordsets成员值
        if response.responseHeader.retCode == 666 and pb_request.history_data_object_names[0] == 'obj_name':
            check_result = 'success'
        else:
            check_result = 'failed'
        result = dict(
            case_id=case_id,                    # 用例id
            date=date,                          # 日期时间
            status='结束',                       # 用例执行状态
            exec_point='end',                   # 用例执行指针（异常时记录执行到哪一步）
            result_code=result_code,            # 返回码
            totle_time=totle_time,              # 用例执行耗时
            check_case=check_case,              # 结果校验规则
            check_result=check_result,          # 校验结果
            data_count=data_count,              # 记录条数
        )
        return result
    else:
        result = dict(
            case_id=case_id,
            date=date,
            status='结束,未校验',
            exec_point='end',
            result_code=result_code,
            totle_time=totle_time,
            check_case=check_case,
            check_result=check_result,
        )
        return result


def sync_subscribe_history_data_object_record_sets(default={}):
    pass


def async_get_history_data_object_record_sets(default={}):
    """
    异步查询历史数据记录的用例实现:

    定义回调函数
    创建API实例并初始化
    连接服务

    构造请求参数
    调用请求方法，发送异步请求
    等待回调函数的处理结果

    回调函数被调用或等待超时
    统计输出测试结果
    测试结束
    :param default: csv读入数据,dict类型
    :return: 测试结果数据，dict类型
    """
    case_id = default.get('case_id')
    date = now()
    flag = False    # 回调触发标志位
    check_case = str(default.get('check'))
    check_result = '未校验'
    data_count = 0      # 不能省略

    def callback(handle, pb_response):
        """
        ！！！ 回调里必须保证异常时能正常返回，否则主进程无法退出！！！
        响应结果验证
        :param handle: c_void_p类型
        :param pb_response: PBResponse类型指针
        :return:
        """

        nonlocal flag, check_result, test_et, data_count
        flag = True
        test_et = time.time()

        data = pb_response.contents     # 获取指针指向的数据
        data_length = data.responseBody.len
        byte_data = data.responseBody.data[:data_length]      # 二进制格式的PB响应数据
        # pb_response = history_pb2.GetHistoryDataObjectRecordSetsResponse()
        pb_request = history_pb2.GetHistoryDataObjectRecordSetsRequest()        # 测试用临时写法
        # pb_response.ParseFromString(byte_data)      # 反序列为pb格式的响应对象
        try:
            print(byte_data)
            pb_request.ParseFromString(byte_data)                                   # 测试用临时写法
        except:
            check_result = 'failed'
            logger.error('unserialize error ！！！')
            logger.error(traceback.format_exc())
            return
        # object_recordsets = pb_response.object_recordsets
        # data_count = len(object_recordsets)
        # 验证object_recordsets成员值及记录条数等
        if data.responseHeader.retCode == 666:      # 自行测试用，实际校验逻辑应以api具体实现为准
            check_result = 'success'
        else:
            check_result = 'failed'

    api = API(default)

    request = history_pb_requests.get_history_data_object_record_set_request(default)
    print(request.get('data'))
    res = api.async_pb_blob_request_call(callback, request)
    result_code = res.get('result_code')
    test_st = res.get('st', 0)
    test_et = res.get('et', 0)
    if result_code == 1:
        st = time.time()
        et = time.time()
        while et - st < 600:        # 等待回调函数被执行，超时时间为10分钟
            if flag:
                break
            time.sleep(1)
            et = time.time()
        result = dict(
            case_id=case_id,
            date=date,
            status='结束',
            exec_point='end',
            result_code=result_code,
            totle_time=test_et - test_st,
            check_case=check_case,
            check_result=check_result,
            data_count=data_count,
        )
        return result
    else:
        result = dict(
            case_id=default.get('case_id'),
            date=date,
            status='结束,未校验',
            exec_point='end',
            result_code=result_code,
            check_case=check_case,
            check_result=check_result,
        )
        return result


def async_subscribe_history_data_object_record_sets(default={}):
    """
    异步订阅历史数据记录的用例实现:

    注册订阅回调

    定义回调函数
    创建API实例并初始化
    连接服务

    构造请求参数
    调用请求方法，发送异步请求
    等待回调函数的处理结果

    回调函数被调用或等待超时
    首次订阅结果校验

    触发订阅
    结果校验

    统计输出测试结果
    测试结束
    :param default: csv读入数据,dict类型
    :return: 测试结果数据，dict类型
    """
    case_id = default.get('case_id')
    date = now()
    flag = False  # 异步回调触发标志位
    sub_flag = False    # 订阅回调触发标志位
    check_case = str(default.get('check'))
    first_check_result = '未校验'
    second_check_result = '未校验'
    first_data_count = 0
    second_data_count = 0

    def subscribe_callback(handle, pb_response_batch):
        nonlocal sub_flag, second_data_count, second_check_result, sub_et
        sub_flag = True
        sub_et = time.time()      # 计时与推送机制有关，如果不分包，只调用一次，那么这种计时方式正确；如果分包，需要统计记录条数到达校验值时再计时
        data = pb_response_batch.contents
        response_count = data.responseCount
        response_array = data.responseArray
        record_sets = []
        try:
            for response in response_array:
                data_length = response.responseBody.len
                byte_data = response.responseBody.data[:data_length]
                pb_response = history_pb2.SubscribeHistoryDataObjectRecordSetsResponse()
                pb_response.ParseFromString(byte_data)  # 反序列为pb格式的响应对象
                object_recordsets = pb_response.object_recordsets
                record_sets.extend(object_recordsets)
        except:
            second_check_result = 'failed'
            logger.error('unserialize error ！！！')
            logger.error(traceback.format_exc())
            return
        second_data_count = len(record_sets)  # 伪代码,不一定这么写，看具体对象结构
        # 验证record_sets成员值及记录条数等
        if 1:
            second_check_result = 'success'
        else:
            second_check_result = 'failed'

    def callback(handle, pb_response):
        nonlocal flag, first_check_result, test_et, first_data_count
        flag = True
        test_et = time.time()
        data = pb_response.contents  # 获取指针指向的数据
        data_length = data.responseBody.len
        byte_data = data.responseBody.data[:data_length]  # 二进制格式的PB响应数据
        pb_response = history_pb2.SubscribeHistoryDataObjectRecordSetsResponse()
        try:
            pb_response.ParseFromString(byte_data)  # 反序列为pb格式的响应对象
        except:
            first_check_result = 'failed'
            logger.error('unserialize error ！！！')
            logger.error(traceback.format_exc())
            return
        object_recordsets = pb_response.object_recordsets
        first_data_count = len(object_recordsets)  # 伪代码,不一定这么写，看具体对象结构
        # 验证object_recordsets成员值及记录条数等
        if 1:
            first_check_result = 'success'
        else:
            first_check_result = 'failed'

    api = API(default)

    res = api.register_subscribe_callback(subscribe_callback, default)
    result_code = res.get('result_code')
    if result_code != 1:        # 注册回调失败
        result = dict(
            case_id=default.get('case_id'),
            date=date,
            status='未结束',
            exec_point='注册回调',
            result_code=result_code,
            check_case=check_case,
            check_result=first_check_result,
        )
        return result
    request = history_pb_requests.subscribe_history_data_object_record_sets(default)
    res = api.async_pb_blob_request_call(callback, request)
    result_code = res.get('result_code')
    test_st = res.get('st', 0)
    test_et = res.get('et', 0)
    if result_code == 1:
        st = time.time()
        et = time.time()
        while et - st < 600:    # 等待首次订阅结果
            if flag:
                break
            time.sleep(3)
            et = time.time()
        if flag and (first_check_result == 'success'):        # 发起二次订阅
            request = history_pb_requests.add_history_data_object_record_sets(default)      # 增加记录触发订阅
            res = api.sync_pb_blob_request_call(request)
            sub_st = res.get('st', 0)       # 增加的起始时间为触发订阅的起始计时时间
            sub_et = res.get('et', 0)
            add_code = res.get('result_code')
            if add_code == 1:       # 增加成功
                query_time = test_et - test_st
                st = time.time()
                et = time.time()
                while et - st < 600:  # 等待二次订阅结果
                    if sub_flag:
                        break
                    time.sleep(3)
                    et = time.time()
                if sub_flag:
                    sub_time = sub_et - sub_st
                else:
                    sub_time = sub_et - sub_st + 600
                # 这里执行取消订阅逻辑
                result = dict(
                    case_id=case_id,
                    date=date,
                    status='结束',
                    exec_point='end',
                    result_code=result_code,
                    query_time=query_time,
                    sub_time=sub_time,
                    check_case=check_case,
                    first_check_result=first_check_result,
                    first_data_count=first_data_count,
                    second_check_result=second_check_result,
                    second_data_count=second_data_count,
                )
                return result
            else:
                # 这里执行取消订阅逻辑
                result = dict(
                    case_id=case_id,
                    date=date,
                    status='未结束',
                    exec_point='增加记录触发二次订阅',
                    result_code=add_code,
                    query_time=test_et - test_st,
                    check_case=check_case,
                    first_check_result=first_check_result,
                    first_data_count=first_data_count,
                    second_check_result=second_check_result,
                )
                return result
        else:
            # 这里执行取消订阅逻辑
            result = dict(
                case_id=case_id,
                date=date,
                status='未结束',
                exec_point='首次订阅',
                result_code=result_code,
                query_time=test_et - test_st,
                check_case=check_case,
                check_result=first_check_result,
                data_count=first_data_count,
            )
            return result
    else:
        result = dict(
            case_id=default.get('case_id'),
            date=date,
            status='未结束',
            exec_point='首次订阅',
            result_code=result_code,
            check_case=check_case,
            check_result=first_check_result,
        )
        return result


CASES_DICT['SyncGetHistoryDataObjectRecordSets'] = sync_get_history_data_object_record_sets
CASES_DICT['ASyncGetHistoryDataObjectRecordSets'] = async_get_history_data_object_record_sets
CASES_DICT['ASyncSubscribeHistoryDataObjectRecordSets'] = async_subscribe_history_data_object_record_sets
