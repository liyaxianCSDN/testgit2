# -*- coding:utf-8 -*-

from ctypes import *
import time
import logging
import functools
from api import api_common
import threading
import os
import traceback


logger = logging.getLogger()


def time_it(func):          # 装饰器，统计接口调用耗时（只给出调用前与返回后的时间）
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        st = time.time()
        code = func(*args, **kwargs)
        et = time.time()
        res = dict(result_code=code, st=st, et=et)      # 这里不直接返回st-et是为了便于在用例中灵活统计耗时
        return res
    return wrapper


class Dll(object):          # 框架内部dll封装类，将参数构造与函数调用分离，更精确统计耗时

    def __init__(self, path):
        self.dll = cdll.LoadLibrary(path)

    @time_it
    def api_init(self):
        return self.dll.tsdbAPIInit()

    @time_it
    def api_un_init(self):
        return self.dll.tsdbAPIUnInit()

    @time_it
    def connect(self, option, handle):
        self.dll.tsdbConnect.argtypes = [POINTER(api_common.ServerConnectOption), c_void_p]     #设置函数参数类型
        self.dll.tsdbConnect.restype = c_int
        return self.dll.tsdbConnect(option, handle)

    @time_it
    def connect_by_sgt(self, option, handle):
        self.dll.tsdbConnectBySGT.argtypes = []
        self.dll.tsdbConnectBySGT.restype = c_int
        return self.dll.tsdbConnectBySGT(option, handle)

    @time_it
    def dis_connect(self, handle):
        self.dll.tsdbDisconnect.argtypes = []
        self.dll.tsdbDisconnect.restype = c_int
        return self.dll.tsdbDisconnect(handle)

    @time_it
    def get_connect_status(self, handle, server_connect_status_list):
        self.dll.tsdbGetConnectStatus.argtypes = []
        self.dll.tsdbGetConnectStatus.restype = c_int
        return self.dll.tsdbGetConnectStatus(handle, server_connect_status_list)

    @time_it
    def free_connect_status(self, server_connect_status_list):
        self.dll.tsdbFreeConnectStatus.argtypes = []
        self.dll.tsdbFreeConnectStatus.restype = c_int
        return self.dll.tsdbFreeConnectStatus(server_connect_status_list)

    @time_it
    def sync_pb_blob_request_call(self, handle, request, response):
        self.dll.tsdbSyncPBBlobRequestCall.argtypes = [c_void_p, POINTER(api_common.PBRequest), POINTER(api_common.PBResponse)]
        self.dll.tsdbSyncPBBlobRequestCall.restype = c_int
        return self.dll.tsdbSyncPBBlobRequestCall(handle, request, response)

    @time_it
    def sync_pb_blob_request_batch_call(self, handle, request_batch, response_batch):
        self.dll.tsdbSyncPBBlobRequestBatchCall.argtypes = []
        self.dll.tsdbSyncPBBlobRequestBatchCall.restype = c_int
        return self.dll.tsdbSyncPBBlobRequestBatchCall(handle, request_batch, response_batch)

    @time_it
    def async_pb_blob_request_call(self, handle, request, callback):
        self.dll.tsdbASyncPBBlobRequestCall.argtypes = [c_void_p, POINTER(api_common.PBRequest), api_common.tsdbAsyncPBRequestCallbackFn]
        self.dll.tsdbASyncPBBlobRequestCall.restype = c_int
        return self.dll.tsdbASyncPBBlobRequestCall(handle, request, callback)

    @time_it
    def async_pb_blob_request_batch_call(self, handle, request_batch, callback):
        self.dll.tsdbASyncPBBlobRequestBatchCall.argtypes = []
        self.dll.tsdbASyncPBBlobRequestBatchCall.restype = c_int
        return self.dll.tsdbASyncPBBlobRequestBatchCall(handle, request_batch, callback)

    @time_it
    def free_pb_blob_response(self, response):
        self.dll.tsdbFreePBBlobResponse.argtypes = []
        self.dll.tsdbFreePBBlobResponse.restype = c_int
        return self.dll.tsdbFreePBBlobResponse(response)

    @time_it
    def free_pb_blob_response_batch(self, response_batch):
        self.dll.tsdbFreePBBlobResponseBatch.argtypes = []
        self.dll.tsdbFreePBBlobResponseBatch.restype = c_int
        return self.dll.tsdbFreePBBlobResponseBatch(response_batch)

    @time_it
    def register_subscribe_callback(self, handle, object_type, mode, callback):
        self.dll.tsdbResgisterSubscribeCallback.argtypes = [c_void_p, c_int, c_int, api_common.tsdbSubscribeCallbackFn]
        self.dll.tsdbResgisterSubscribeCallback.restype = c_int
        return self.dll.tsdbResgisterSubscribeCallback(handle, object_type, mode, callback)


def get_pb_request_header():        # 接口函数中C++类型通用参数构造函数
    request_header = api_common.PBRequestHeader()
    # 生成请求头
    return request_header
    pass


def get_connect_option(default={}):         # # 接口函数中C++类型通用参数构造函数
    user_pwd = api_common.TSDB_BLOB()
    server_connect_option = api_common.ServerConnectOption()
    server_address_list = api_common.ServerAddressList()
    server_adress = api_common.ServerAdress()
    server_adress.instanceCount = default.get('instance_count', 1)
    instance_array_class = api_common.ServerInstanceAddress * server_adress.instanceCount        # 定义长度为‘instanceCount’的server_address数组
    instance_array = instance_array_class()
    for i in range(server_adress.instanceCount):
        instance_array[i].instanceName = default.get('instance_names')[i].encode('utf-8')  # 此处考虑固化实例配置信息
        instance_array[i].instanceIP = default.get('instance_ips')[i].encode('utf-8')
        instance_array[i].instanceBackupIP = default.get('instance_backupips')[i].encode('utf-8')
        instance_array[i].redundancyInstanceIP = default.get('instance_redundancy_ips')[i].encode('utf-8')
        instance_array[i].redundancyInstanceBackupIP = default.get('instance_redundancy_backupips')[i].encode('utf-8')
        instance_array[i].port = default.get('instance_port', 9092)
    server_adress.instanceAddressList = instance_array
    server_address_list.serverCount = default.get('server_count', 1)
    server_array_class = api_common.ServerAdress * server_address_list.serverCount
    server_array = server_array_class()

    # 这里为简单默认每个服务的实例个数、配置信息完全相同（实际IP应该会不一样）
    for j in range(server_address_list.serverCount):
        server_array[j] = server_adress
    server_address_list.serverAddressList = server_array
    bit_pwd = default.get('user_pwd', 'Kingview01').encode('utf-8')
    user_pwd.len = len(bit_pwd)
    user_pwd.data = bit_pwd
    server_connect_option.userName = default.get('user_name', 'sys_user1').encode('utf-8')
    server_connect_option.userPassword = user_pwd
    server_connect_option.serverAddressList = server_address_list
    server_connect_option.connectProtocal = default.get('connect_protocal', 3)      # 枚举直接给int值
    server_connect_option.connectOption = default.get('connect_option', 1)
    server_connect_option.applicationName = default.get('application_name', 'history').encode('utf-8')
    server_connect_option.osName = default.get('os_name', 'centos7').encode('utf-8')
    server_connect_option.userName = default.get('user_name', 'sys_user1').encode('utf-8')
    return server_connect_option


# 单例模式，线程安全，对外提供的API，各子系统进行用例开发时，实例化该类后直接调用提供的对象方法即可
class API(object):
    __thread_lock = threading.Lock()
    __connect_state = False

    def __init__(self, default):
        '''
        :param default: dict
        '''
        pass

    def __new__(cls, *args, **kwargs):

        if not hasattr(cls, '_instance'):
            with cls.__thread_lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = object.__new__(cls)
                    cls._instance.__init_api(args[0])
        return cls._instance

    def __init_api(self, default={}):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tsdbTestAPI.dll')
        self._DLL = Dll(path)
        self._handle = c_void_p()
        self._connect_option = get_connect_option(default)
        self.api_init()

    def api_init(self):
        pass

    def api_un_init(self):
        pass

    def connect(self):
        if not self.__connect_state:
            with self.__thread_lock:
                if not self.__connect_state:
                    handle = byref(self._handle)
                    connect_option = pointer(self._connect_option)
                    try:
                        res = self._DLL.connect(connect_option, handle)
                    except:
                        res = dict(result_code=-1)
                        logger.error(traceback.format_exc())
                    if res.get('result_code') == 1:
                        self.__connect_state = True
                    return res
                else:
                    res = {'result_code': 1}
                    return res
        else:
            res = {'result_code': 1}
            return res

    def connect_by_sgt(self):
        pass

    def dis_connect(self):
        self.__connect_state = False
        pass

    def get_connect_status(self):
        pass

    def free_connect_status(self):
        pass

    def sync_pb_blob_request_call(self, default={}):
        pb_request = api_common.PBRequest()
        pb_response = api_common.PBResponse()
        pb_request.requestHeader = get_pb_request_header()
        request_body = api_common.TSDB_BLOB()
        request_body.len = default.get('size')
        request_body.data = default.get('data')
        pb_request.requestBody = request_body
        try:
            res = self._DLL.sync_pb_blob_request_call(self._handle, byref(pb_request), byref(pb_response))
        except:
            res = dict(result_code=-1)
            logger.error(traceback.format_exc())
        code = res.get('result_code', -1)
        if code == 1:   # 假设返回1表示执行成功
            msg = 'sync_' + default.get('request_name') + ' success!'
            logging.info(msg)
        else:
            msg = 'sync_' + default.get('request_name') + ' failed! result_code:%d' % code
            logging.info(msg)
        res['response'] = pb_response
        return res

    def sync_pb_blob_request_batch_call(self):
        pass

    def async_pb_blob_request_call(self, func, default={}):
        pb_request = api_common.PBRequest()
        pb_request.requestHeader = get_pb_request_header()
        request_body = api_common.TSDB_BLOB()
        request_body.len = default.get('size')
        request_body.data = default.get('data')
        pb_request.requestBody = request_body
        callback = api_common.tsdbAsyncPBRequestCallbackFn(func)
        try:
            res = self._DLL.async_pb_blob_request_call(self._handle, byref(pb_request), callback)     # 目前的API代码中异步接口有返回值，先按有返回值处理；如有改动，再修改
        except:
            res = dict(result_code=-1)
            logger.error(traceback.format_exc())
        code = res.get('result_code', -1)
        if code == 1:  # 假设返回1表示执行成功
            msg = 'async_' + default.get('request_name') + ' success!'
            logging.info(msg)
        else:
            msg = 'async_' + default.get('request_name') + ' failed! result_code:%d' % code
            logging.info(msg)
        return res

    def async_pb_blob_request_batch_call(self, func):
        pass

    def free_pb_blob_response(self):
        pass

    def free_pb_blob_response_batch(self):
        pass

    def register_subscribe_callback(self, func, default={}):
        object_type = default.get('object_type', 1)     # int型
        mode = default.get('mode', 0)   # int型
        callback = api_common.tsdbSubscribeCallbackFn(func)
        try:
            res = self._DLL.register_subscribe_callback(self._handle, object_type, mode, callback)
        except:
            res = dict(result_code=-1)
            logger.error(traceback.format_exc())
        code = res.get('result_code', -1)
        if code == 1:  # 假设返回1表示执行成功
            msg = 'async_' + default.get('case_id') + ' success!'
            logging.info(msg)
        else:
            msg = 'async_' + default.get('case_id') + ' failed! result_code:%d' % code
            logging.info(msg)
        return res





