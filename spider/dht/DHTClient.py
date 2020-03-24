from collections import deque

from .DHTSender import DHTSender
from ..util.common import random_nid, get_neighbor
from ..util.common import ran_str
from ..config import Config

# DHTClient 继承于 DHTSender类
class DHTClient(DHTSender):
    '''
        DHT网络的客户端，用于模拟KRPC协议
    '''
    def __init__(self, bind_ip, bind_port):
        DHTSender.__init__(self, bind_ip, bind_port)
        # 绑定ip和port
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        # 随机生成nid
        self.nid = random_nid()
        # 双端队列，用来装扩散路由时返回的节点
        self.nodes = deque(maxlen=Config.MAX_NODE_SIZE)
        # 守护线程

    #加入DHT网络，进行路由扩散
    def join_dht(self):
        for address in Config.BOOTSTRAP_NODES:
            self.send_find_node(address)

    # 模拟KRPC协议中的find_node请求模拟
    def send_find_node(self, address, tar_nid=None):
        # 判断是进行路由扩散还是加入DHT
        # nid = tar_nid if tar_nid else self.nid
        # 随机生成长度为2的tid
        tid = ran_str(2)
        msg = {
            'tid': tid,
            'y': 'q',
            'q': 'find_node',
            'id': self.nid,
            'target': random_nid() if tar_nid==None else tar_nid
        }
        # 发送find_node krpc
        print('发送find_node请求')
        print('msg: {0} \n to address: {1}'.format(msg, address))
        self.send_krpc(msg, address)






