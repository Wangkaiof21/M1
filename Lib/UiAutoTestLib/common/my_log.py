import os
import logging
from logging.handlers import TimedRotatingFileHandler
from common.settings import LOGGING
from common.COM_path import *
file_path = os.path.join(path_LOG_MY, LOGGING.get('log_name'))

def create_logger():
    """创建日志收集器"""
    mylog = logging.getLogger("charpters")
    mylog.setLevel(LOGGING.get('level'))

    fh = TimedRotatingFileHandler(file_path, when='d',
                                  interval=1, backupCount=1,
                                  encoding="utf-8")
    fh.setLevel(LOGGING.get('fh_level'))
    mylog.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(LOGGING.get('sh_level'))
    mylog.addHandler(sh)

    formatter = "%(asctime)s - [%(filename)s-->line:%(lineno)d] - %(levelname)s: %(message)s"
    mate = logging.Formatter(formatter)

    fh.setFormatter(mate)
    sh.setFormatter(mate)

    return mylog

mylog = create_logger()