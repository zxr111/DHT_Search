import socket
from time import sleep
from collections import deque


from .DHTClient import DHTClient
from ..config import Config
from ..util.common import random_nid, get_neighbor, timer
from ..util import bcode
from ..util.common import decode_nodes
from .NODE import NODE
from ..database.Redis import RedisClient2


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
            'get_peers': self.on_get_peers_request,
            'announce_peer': self.on_announce_peer_request,
        }
        # 定时器，定时重新加入DHT网络
        timer(Config.REJOIN_DHT_INTERVAL, self.rejoin_dht)

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
                #回复收到的信息
                self.on_message(msg, address)
            except Exception:
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
                    self.process_request_actions[msg['q']](msg, address)
                except KeyError:
                    pass

        except Exception:
            pass

    # 处理find_node的response
    def on_find_node_response(self, msg):
        for node in decode_nodes(msg['r']['nodes']):
            try:
                (nid, ip, port) = node
                if len(nid) != 20:
                    print('nid格式出错')
                    continue
                if ip == self.bind_ip:
                    print('不能回复自身')
                    continue
                n = NODE(nid, ip, port)
                #self.Redis.add_node(node)
                print('收到node :{0} 加入双端队列中'.format(node))
                self.nodes.append(n)
                RedisClient2.add_peer(nid, (ip, port))
                # self.send_find_node(address, nid)
            except KeyError:
                print('存入节点出错')


    # 处理get_peers请求函数
    def on_get_peers_request(self, msg, address):
        print('收到get_peers request msg : {0}'.format(msg))
        try:
            h = msg['a']['info_hash']
            tid = msg['t']
            token = h[:2]
            msg = {
                't': tid,
                'y': 'r',
                'r': {
                    'id': get_neighbor(h, self.nid),
                    'nodes': '',
                    'token': token
                }
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass

    #处理announce_peer请求
    def on_announce_peer_request(self, msg, address):
        print('收到announce_peer request msg : {0}'.format(msg))
        try:
            h = msg['a']['info_hash']
            token = msg['a']['token']
            if h[:2] == token:
                if 'implied_port ' in msg['a'] and msg['a']['implied_port '] != 0:
                    port = address[1]
                else:
                    port = msg['a']['port']
                #self.pool.submit(download_metadata, (address[0], port), h, self.process_id)
        except Exception:
            return
        finally:
            self.ok(msg, address)

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
