

import logging
from logging import handlers
from functools import lru_cache


@lru_cache(maxsize=16)
def init_logger(name=''):
    # create logger
    logger = logging.getLogger(name)
    # logger.setLevel(logging.DEBUG)      # 设置输出控制台的日志等级
    # # 配置控制台输出
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')     # create formatter
    # ch.setFormatter(formatter)        # add formatter to ch
    # logger.addHandler(ch)             # add ch to logger
    # 配置日志输出文件
    # file = logging.FileHandler('./logs/sys.log', mode='a')
    file = handlers.TimedRotatingFileHandler('./logs/sys.log', when='D')
    file.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file.setFormatter(formatter)
    logger.addHandler(file)
    return logger
    