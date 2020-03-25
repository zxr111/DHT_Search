import socket
from time import sleep
from collections import deque


from .DHTClient import DHTClient
from ..config import Config
from ..util.common import random_nid, get_neighbor
from ..util import bcode
from ..util.common import decode_nodes
from .NODE import NODE
from ..database.Redis import RedisClient


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
        # 回复方法
        self.process_request_actions = {
            'ping': self.on_ping_request,
            'get_peers': self.on_get_peers_request,
            'announce_peer': self.on_announce_peer_request,
            'find_node': self.on_find_node_request
        }


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
            # 如果收到请求为quest
            elif msg['y'] == 'q':
                try:
                    # if msg['y']['q'] == 'get_peers':
                    #     self.on_get_peers_request(msg, address)
                    # elif msg['y']['q'] == 'announce_peer':
                    #     print('收到announce_peer request')
                    # elif msg['y']['q'] == 'find_node':
                    #     print('收到find_node request')
                    # elif msg['y']['q'] == 'ping':
                    #     print('收到ping request')
                    #     self.ok(msg, address)
                    self.process_request_actions[msg['y']['q']](msg, address)
                except KeyError:
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

    def on_find_node_request(self, msg, address):
        print('收到find_node request')

    # 自动向双端队列中的节点发送find_node请求
    def auto_send_find_node(self):
        while True:
            try:
                # 从双端队列中取出node
                node = self.nodes.popleft()
                print('取出node: {0}, {1}, {2}'.format(node.nid, node.ip, node.port))
                address = (node.ip, node.port)
                # 向取出的node请求寻找新的节点
                self.send_find_node(address, node.nid)
            except IndexError:
                pass
            # 发送间隔
            sleep(1.0 / Config.MAX_NODE_SIZE)

    # 处理get_peers请求函数
    def on_get_peers_request(self, msg, address):
        print('收到get_peers request')
        try:
            h = msg['a']['info_hash']
            print('收到get_peers request info_hash : {0}'.format(h))
            tid = msg['t']
            token = h[:2]
            msg = {
                't': tid,
                'y': 'r',
                'r': {
                    # 'id': get_neighbor(h, self.nid),
                    'id': self.nid,
                    'nodes': '',
                    'token': token
                }
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass
    # 处理ping请求
    def on_ping_request(self, msg, address):
        print('收到ping请求')
        self.ok(msg, address)

    def on_announce_peer_request(self, msg, address):
        print('收到annoucne_peer request')

    # 回复成功消息
    def ok(self, msg, address):
        try:
            tid = msg['t']
            nid = msg['a']['id']
            msg = {
                't': tid,
                'y': 'r',
                'r': {
                    'id': get_neighbor(nid, self.nid)
                }
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass
