# !/usr/bin/python 3.6
# -*-coding:utf-8-*-

import os
import sys

import yaml
import logging

# 配置文件的目录，可以根据需要修改，默认为env.py所在的目录
BASE_PATH = os.getcwd()

# 测试环境配置文件路径
CONFIG_SIT = "config_sit.yaml"
# 本地开发环境配置文件路径
CONFIG_LOCAL = "config_local.yaml"
# 生产环境配置文件路径
CONFIG_PRO = "config_pro.yaml"

# 根据环境修改, 比如使用测试环境路径
CONFIG_PATH = os.path.join(BASE_PATH, CONFIG_LOCAL)


######################################
#         读取配置文件                #
######################################
def get_configuration():
    """
    Get configuration file

    Args:
    config_path (str): configuration path, xx.yaml

    Return:
    config (dict)    : configuration file as dictionary format

    Raise:
    IO error
    """
    if not os.path.exists(CONFIG_PATH):
        error_msg = "Configuration file {} does not exists!".format(CONFIG_PATH)
        logging.error(error_msg)
        raise IOError(error_msg)
    else:
        with open(CONFIG_PATH, "rt", encoding='utf8') as f:
            config = yaml.safe_load(f.read())
    return config
