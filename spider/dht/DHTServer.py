import socket
from asyncio import sleep
from collections import deque


from .DHTClient import DHTClient
from ..config import Config
from ..util.common import random_nid
from ..util import bcode
from ..util.common import decode_nodes
from .NODE import NODE


# DHTServer 继承于 DHTClient类
class DHTServer(DHTClient):
    '''
        DHT网络服务类
        用于回复KRPC请求
    '''
    def __init__(self, bind_ip, bind_port, process_id):
        DHTClient.__init__(self, bind_ip, bind_port)
        self.process_id = process_id
        # 绑定ip和port
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        # 随机生成nid
        self.nid = random_nid()
        # 双端队列，用来装扩散路由时返回的节点
        self.nodes = deque(maxlen=Config.MAX_NODE_SIZE)


    def run(self):
        # 初始化DHT网络
        print('初始化DHT网络')
        self.join_dht()
        print('监听中。。。')
        while True:
            try:
                # 从socket中获取缓存数据
                (data, address) = self.udp.recvfrom(65536)
                msg = bcode.bdecode(data)
                print('收到信息msg: {0} \n from address: {1}'.format(msg, address))
                print(msg['r']['nodes'])
                #回复收到的信息
                self.on_message(msg, address)
            except Exception:
                print('监听出错')
                pass

    # 处理收到的KRPC请求
    def on_message(self, msg, address):
        try:
            # 接收到的请求为response
            if msg['y'] == 'r':
                # 如果有返回的路由节点，则向这些节点继续发送find_node请求
                # 进行路由扩散
               if 'nodes' in msg['r']:
                    self.on_find_node_response(msg)
            elif msg['y'] == 'q':
                if msg['y']['q'] == 'find_node':
                    pass
                elif msg['y']['q'] == 'get_peers':
                    pass
                elif msg['y']['q'] == 'announce_peer':
                    pass
        except Exception:
            pass

    # 处理find_node的response
    def on_find_node_response(self, msg):
        for node in decode_nodes(msg['r']['nodes']):
            (nid, ip, port) = node
            if len(nid) != 20:
                print('nid格式出错')
                continue
            if ip == self.bind_ip:
                print('不能回复自身')
                continue
            n = NODE(nid, ip, port)
            self.nodes.append(n)
            # self.send_find_node(address, nid)
            print('收到node: {0}'.format(str(node)))

    # 自动向双端队列中的节点发送find_node请求
    def auto_send_find_node(self):
        while True:
            try:
                # 从双端队列中取出node
                node = self.nodes.popleft()
                print('取出node: {0}, {1}, {2}'.format(node.nid, node.ip, node.port))
                address = (node.ip, node.port)
                self.send_find_node(address, node.nid)
            except IndexError:
                pass
            # 发送间隔
            sleep(1.0 / Config.MAX_NODE_SIZE)
