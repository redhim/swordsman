# -*- coding: utf-8 -*-
"""
发送和接收post/get请求，并且获取响应数据的模块
"""

from urllib3 import PoolManager
import time
import json
from log import logger


def request(request_type, url, headers, body, code_name):
    """
     发送post/get请求，并且获取响应数据的模块
     request_type,请求的类型
     url,请求地址
     headers,请求头
     body,请求的数据
     code_name,响应数据的编码方式
    """
    resp_data = None  # 返回的响应数据
    manager = PoolManager()
    for i in range(3):
        try:
            resp = manager.request(request_type, url, headers=headers, body=body)
            if str(resp.status) == '200':
                resp_data = resp.data.decode(code_name)
                break
            else:
                logger.error('请求地址%s状态码不是200' % url)
                time.sleep(0.5)
        except Exception as e:
            logger.error('请求地址%s失败,原因%s' % (url, repr(e)))
            time.sleep(0.5)
    return resp_data


def json_post(url, json_dict, code_name='utf-8'):
    """
     发送post请求，并且获取响应数据的模块
     url,请求地址
     json_dict,发送的json数据
     code_name,响应数据的编码方式
    """
    # 请求头信息
    headers = {
        'Content-Type': 'application/json'
    }

    # 处理请求数据
    try:
        data_str = json.dumps(json_dict)
        data = bytes(data_str, code_name)
    except Exception as e:
        logger.info('解析请求json数据%s失败,原因%s' % (json_dict, repr(e)))

    # 发送post请求
    logger.info('请求地址:%s' % url)
    logger.info('请求内容:%s' % json.dumps(json_dict, ensure_ascii=False))
    resp_str = request('post', url, headers, data, code_name)
    # 处理响应数据
    resp_dict = {}
    try:
        resp_dict = json.loads(resp_str)
    except Exception as e:
        logger.info('解析响应json数据%s失败,原因%s' % (resp_str, repr(e)))
    logger.info('响应内容:%s' % (resp_str))
    return resp_dict
