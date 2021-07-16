import logging
import os
from logging.config import fileConfig

BASE = os.getcwd()


def init_logger(name):
    __log_main_path = os.getcwd() + "/.logs/info.log"
    __log_dbg_path = os.getcwd() + "/.logs/dbg.log"
    __create_files([str(__log_main_path), str(__log_dbg_path)])

    fileConfig(f"{BASE}/config/logger.ini", disable_existing_loggers=False)
    logger = logging.getLogger(name)

    __set_levels()

    return logger


def __create_files(paths: list):
    for path in paths:
        __basedir = os.path.dirname(path)
        if not os.path.exists(__basedir):
            os.makedirs(__basedir)
            open(path, "a").close()


def __set_levels():
    logging.getLogger("chardet.charsetprober").setLevel(logging.ERROR)
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger("boto3").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("requests_oauthlib").setLevel(logging.ERROR)
