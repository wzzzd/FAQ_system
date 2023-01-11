
import time
import datetime
from datetime import timedelta, datetime
# from config.webcheck_config import get_settings
import logging


# logger = get_settings().logger


def excute_time(func_name=''):
    """装饰器，记录程序运行时长"""
    def decorator(func):
        def wrapper(*args, **kw):
            logging.info('【{0}】function start'.format(func_name))
            s_time = time.time()
            result = func(*args, **kw)
            cost_time = time.time() - s_time
            logging.info('【{0}】function end >> cost time: {1}s'.format(func_name, cost_time))
            return result
        return wrapper
    return decorator



def get_date(day=0, format='%Y%m%d'):
    """获取日期"""
    yesterday = datetime.today() + timedelta(day)
    yesterday_format = yesterday.strftime(format)
    return yesterday_format



