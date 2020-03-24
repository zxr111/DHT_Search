import logging
from hashlib import sha1
from random import randint

# 随机生成nid
from struct import unpack

from _socket import inet_ntoa

# 日志等级
LOG_LEVEL = logging.INFO

def random_nid():
    hash = sha1()
    # nid长度为20字节，40个16进制数
    hash.update(ran_str(40).encode('utf-8'))
    return hash.digest()

# 随机生成字符串
def ran_str(length):
    return ''.join(chr(randint(0, 255)) for _ in range(length))

# 解码回复信息中的nodes
def decode_nodes(nodes):
    n = []
    length = len(nodes)
    if (length % 26) != 0:
        return n
    for i in range(0, length, 26):
        nid = nodes[i:i + 20]
        ip = inet_ntoa(nodes[i + 20:i + 24])
        port = unpack('!H', nodes[i + 24:i + 26])[0]
        n.append((nid, ip, port))
    return n

def get_neighbor(target, nid, end=10):
    """
    生成随机 target 周边节点 id，在 Kademlia 网络中，距离是通过异或(XOR)计算的，
    结果为无符号整数。distance(A, B) = |A xor B|，值越小表示越近。

    :param target: 节点 id
    """
    return target[:end] + nid[end:]

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
