#!/usr/bin/env python3
# encoding: utf-8

import os


class Config(object):

    ################入库程序配置###################
    #任务执行时间(秒)
    #STORAGE_TASK_TIME = 10
    ################redis配置##################
    # redis 地址
    REDIS_HOST = "127.0.0.1"
    # redis 端口
    REDIS_PORT = 6379
    # redis 密码
    REDIS_PASSWORD = 123456
    # redis 连接池最大连接量
    REDIS_MAX_CONNECTION = 20

    ################elasticsearch配置##################
    #elastics 索引名称
    ELASTICS_INDEX_NAME = 'bt_metadata'
    #elastics 索引类型
    ELASTICS_INDEX_TYPE = 'doc'
    # elastics 地址
    ELASTICS_HOST = "127.0.0.1"
    # elastics 端口
    ELASTICS_PORT = 9200
    # elastics 用户名
    ELASTICS_USER_NAME = 'root'
    # elastics 密码
    ELASTICS_PASSWORD = ''
    # elastics 连接池最大连接量
    ELASTICS_MAX_CONNECTION = 20
