#!/usr/bin/env python3
# encoding: utf-8

import logging
import datetime

# 日志等级
LOG_LEVEL = logging.INFO

def get_logger(logger_name):
    """
    返回日志实例
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)
    fh = logging.StreamHandler()
    fh.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(fh)
    return logger

# 字节到标准文件大小转换
def str_of_size(size):
    '''
    递归实现，精确为最大单位值 + 小数点后三位
    '''
    def strofsize(integer, remainder, level):
        if integer >= 1024:
            remainder = integer % 1024
            integer //= 1024
            level += 1
            return strofsize(integer, remainder, level)
        else:
            return integer, remainder, level

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    integer, remainder, level = strofsize(size, 0, 0)
    if level+1 > len(units):
        level = -1
    return ( '{}.{:>03d} {}'.format(integer, remainder, units[level]) )

# 文件格式标准化
def file_format_stand(data):
    ctime_stamp = data['_source']['create_time']
    utime_stamp = data['_source']['update_time']
    dateArray = datetime.datetime.fromtimestamp(ctime_stamp)
    data['_source']['create_time'] = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    dateArray = datetime.datetime.fromtimestamp(utime_stamp)
    data['_source']['update_time'] = dateArray.strftime("%Y-%m-%d %H:%M:%S")

    # 修改文件大小为标准格式
    data['_source']['file_size'] = str_of_size(data['_source']['file_size'])
    # 修改文件列表每个文件大小为标准格式
    file_list = eval(data['_source']['file_list'])
    for i in range(len(file_list)):
        file_list[i]['l'] = str_of_size(file_list[i]['l'])
    data['_source']['file_list'] = str(file_list)

    # 修改文件类型
    switch = {
        0: '视频',
        1: '音频',
        2: '图片',
        3: '文档',
        4: '二进制文件',
        5: '存档文件',
        6: '其他'
    }
    data['_source']['file_type'] = switch.get(data['_source']['file_type'])

    return data

# 批量修改文件格式
def bulk_ffs(datas):
    for i in range(len(datas)):
        datas[i] = file_format_stand(datas[i])

    return datas


