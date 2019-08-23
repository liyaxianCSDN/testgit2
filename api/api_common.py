# coding:utf8

from ctypes import *

# ！！！ 以下各种指针类型指向的内存块均为只读的，对于需要输入内存块保存输出值，需要可写的内存块，使用create_string_buffer()函数创建


class TSDB_TIMESTAMP(Structure):
    _fields_ = [('seconds', c_long), ('nanos', c_int)]


class TSDB_BLOB(Structure):
    _fields_ = [('len', c_uint), ('data', c_char_p)]


class ServerInstanceAddress(Structure):
    _fields_ = [
        ('instanceName', c_char_p),
        ('instanceIP', c_char_p),
        ('instanceBackupIP', c_char_p),
        ('redundancyInstanceIP', c_char_p),
        ('redundancyInstanceBackupIP', c_char_p),
        ('port', c_int)
    ]


class ServerAdress(Structure):
    _fields_ = [
        ('serverName', c_char_p),
        ('instanceCount', c_uint),
        ('instanceAddressList', POINTER(ServerInstanceAddress))
    ]


class ServerAddressList(Structure):
    _fields_ = [
        ('serverCount', c_uint),
        ('serverAddressList', POINTER(ServerAdress))
    ]


class ServerInstanceConnectCondition(Structure):
    _fields_ = [
        ('connectStatus', c_int),
        ('lastTransitionTime', TSDB_TIMESTAMP),
        ('lastUpdateTime', TSDB_TIMESTAMP),
        ('reason', c_char_p),
        ('message', c_char_p)
    ]


class ServerInstanceConnectStatus(Structure):
    _fields_ = [
        ('instanceName', c_char_p),
        ('connectStatus', c_int),
        ('conditionCount', c_uint),
        ('connectConditionList', POINTER(ServerInstanceConnectCondition))
    ]


class ServerConnectStatus(Structure):
    _fields_ = [
        ('serverName', c_char_p),
        ('connectStatus', c_int),
        ('instanceCount', c_uint),
        ('instanceConnectStatusList', POINTER(ServerInstanceConnectStatus))
    ]


class ServerConnectStatusList(Structure):
    _fields_ = [
        ('serverCount', c_uint),
        ('serverConnectStatusList', POINTER(ServerConnectStatus))
    ]


class ServerConnectOption(Structure):
    _fields_ = [
        ('userName', c_char_p),
        ('userPassword', TSDB_BLOB),
        ('serverAddressList', ServerAddressList),
        ('connectProtocal', c_int),
        ('connectOption', c_int),
        ('applicationName', c_char_p),
        ('osName', c_char_p)
    ]


class ServerConnectCertificateOption(Structure):
    _fields_ = [
        ('securityServiceSessionID', c_longlong),
        ('serviceSGT', TSDB_BLOB),
        ('clientAuthenticator', TSDB_BLOB),
        ('serverAddressList', ServerAddressList),
        ('connectProtocal', c_int),
        ('connectOption', c_int),
        ('applicationName', c_char_p),
        ('osName', c_char_p)
    ]


class PBRequestHeader(Structure):
    _fields_ = [
        ('requestID', c_longlong),
        ('commandID', c_int),
        ('sessionID', c_longlong),
        ('operatorSessionID', c_longlong),
        ('transactionID', c_longlong),
        ('localOperate', c_char_p)
    ]


class PBRequest(Structure):
    _fields_ = [
        ('requestHeader', PBRequestHeader),
        ('requestBody', TSDB_BLOB)
    ]


class PBRequestBatch(Structure):
    _fields_ = [
        ('requestCount', c_uint),
        ('requestArray', POINTER(PBRequest))
    ]


class PBResponseHeader(Structure):
    _fields_ = [
        ('requestID', c_longlong),
        ('retCode', c_int),
        ('reponseType', c_int),
        ('packetSeq', c_int)
    ]


class PBResponse(Structure):
    _fields_ = [
        ('responseHeader', PBResponseHeader),
        ('responseBody', TSDB_BLOB)
    ]


class PBResponseBatch(Structure):
    _fields_ = [
        ('responseCount', c_uint),
        ('responseArray', POINTER(PBResponse))
    ]


tsdbAsyncPBRequestCallbackFn = CFUNCTYPE(None, c_void_p, POINTER(PBResponse))
tsdbAsyncPBRequestBatchCallbackFn = CFUNCTYPE(None, c_void_p, POINTER(PBResponseBatch))
tsdbSubscribeCallbackFn = CFUNCTYPE(None, c_void_p, POINTER(PBResponseBatch))

