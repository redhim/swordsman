# -*- coding: utf-8 -*-
import uuid
from datetime import datetime


def get_uuid():
    """
        生成32位uuid码
    """
    return str(uuid.uuid1()).replace('-', '')


def now_formate():
    """
         生成   2018-12-30 15:15:15 999 格式的时间字符串
    """
    current_time = datetime.now()
    time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
    millisecond = int(current_time.microsecond * 1e-3)
    return '{} {:0<3d}'.format(time_str, millisecond)
