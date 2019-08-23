# -*- coding:utf-8 -*-

from test_cases import *          # 有用
from settings import CASES_DICT   # 有用
from api.api import API
from common import *
import logging
import socketserver
import traceback

IP_PORT = ('', 6666)            # TCP服务器绑定地址
BUFFER_SIZE = 4096              # 每次接收的最大数据长度(字节)
logger = logging.getLogger()


class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        logger.info(self.request)
        try:
            data = self.request.recv(BUFFER_SIZE)
            clean_data = data.decode('GBK').strip()
            if not clean_data:
                logger.warning('no data ！！！')
                return
            str_input = clean_data.replace(';', ',')
            d_input = eval(str_input)
            case_id = d_input.get('case_id')
            if not case_id:
                logger.error('Unidentified case_id !')
                result = dict(
                    case_id=case_id,
                    date=now(),
                    status='未执行,无法识别的case_id',
                    exec_point='connect',
                    result_code=-1,
                )
                self.request.sendall(str(result).encode('GBK'))
                return
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
                self.request.sendall(str(result).encode('GBK'))
            else:
                funcname = d_input.get('case_id').split('_')[0]
                func = CASES_DICT.get(funcname)
                if not func:
                    logger.error('invalid case_id: %s' % case_id)
                logger.critical('Run Test: %s' % case_id)
                try:
                    result = func(d_input)
                except:
                    result = dict(
                        case_id=case_id,
                        date=now(),
                        status='未知异常，查看日志',
                        exec_point='exec_cases',
                        result_code=-1,
                    )
                    logger.error(traceback.format_exc())
                self.request.sendall(str(result).encode('GBK'))
        except Exception as e:
            logger.error(traceback.format_exc())
            self.request.sendall(str(e).encode('GBK'))


if __name__ == '__main__':
    s = socketserver.ThreadingTCPServer(IP_PORT, RequestHandler)
    s.serve_forever()
