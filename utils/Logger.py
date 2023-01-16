

import logging
from logging import handlers
from functools import lru_cache

import os
import logbook
from logbook import Logger, TimedRotatingFileHandler

logbook.set_datetime_format('local')


# @lru_cache(maxsize=16)
# def init_logger(name='', path='./logs/'):
#     # create logger
#     logger = logging.getLogger(name)
#     # logger.setLevel(logging.DEBUG)      # 设置输出控制台的日志等级
#     # # 配置控制台输出
#     # ch = logging.StreamHandler()
#     # ch.setLevel(logging.DEBUG)
#     # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')     # create formatter
#     # ch.setFormatter(formatter)        # add formatter to ch
#     # logger.addHandler(ch)             # add ch to logger
#     # 配置日志输出文件
#     # file = logging.FileHandler('./logs/sys.log', mode='a')
#     file = handlers.TimedRotatingFileHandler(path+'sys.log', when='D')
#     file.setLevel(logging.INFO)
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     file.setFormatter(formatter)
#     logger.addHandler(file)
#     return logger


@lru_cache(maxsize=16)
def init_logger(path='./logs/'):
    # 初始化日志配置
    log_level: str = 'INFO'
    log_format: str = '{record.time:%Y-%m-%d %H:%M:%S.%f%z}|{record.level_name}|{record.thread_name}|{record.extra[' \
                      'trace_id]}|{record.module}:{record.lineno}|{record.message}'
    logger = Logger('app')
    # setup logger and handler
    log_level = getattr(logbook.base, log_level)
    logger.level = log_level
    log_name = path + '/sys.log'
    if not os.path.exists(path):
        os.makedirs(path)
    handler = TimedRotatingFileHandler(log_name, date_format='%Y-%m-%d')
    handler.format_string = log_format
    handler.push_application()
    return logger



