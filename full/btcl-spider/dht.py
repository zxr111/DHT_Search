#!/usr/bin/env python3
# encoding: utf-8

import socket
from multiprocessing import Process
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from collections import deque
from common.bencode import bencode, bdecode
from common.utils import *
from config import Config
from common.metadata import download_metadata
from common.database import RedisClient2

logger = get_logger("logger_dht_main")

# 接收和发送find_node请求的数据结构
class KNode(object):
    def __init__(self, nid, ip, port):
        # nodeId 为DHT中node的key
        self.nid = nid
        # node对应的ip
        self.ip = ip
        # node 对应的port
        self.port = port

# 封装UDP协议和KRPC协议类
class DHT(Thread):
    def __init__(self,bind_ip,bind_port):
        Thread.__init__(self)
        # socket UDP协议封装
        self.ufd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # 绑定对应线程ip 和 port
        self.ufd.bind((bind_ip, bind_port))

    def send_krpc(self, msg, address):
        # noinspection PyBroadException
        try:
            # KRPC协议需要使用bencode进行传送信息的封装
            self.ufd.sendto(bencode(msg), address)
        except Exception:
            print('krpc发送失败')
            pass

# DHT客户端
class DHTClient(DHT):
    def __init__(self,bind_ip,bind_port):
        DHT.__init__(self,bind_ip,bind_port)
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        # 线程守护进程
        self.setDaemon(True)
        # 随机生成nodeID
        self.nid = random_id()
        # 双端队列，用于存储接收到的nodes信息
        self.nodes = deque(maxlen=Config.MAX_NODE_SIZE)

    # KRPC中的find_node请求
    def send_find_node(self, address, nid=None):
        # 判断进行路由扩散还是加入DHT网络
        nid = get_neighbor(nid, self.nid) if nid else self.nid
        tid = entropy(2)  # 随机生成长度为2的TransactionID,
        msg = {
            't': tid,
            'y': 'q',
            'q': 'find_node',
            'a': {
                'id': nid,
                'target': random_id()
            }
        }
        #print('发送krpc')
        print('发送find_node msg: {0} to address: {1}'.format(msg, address))
        self.send_krpc(msg, address)

    # 初始化DHT网络，加入到DHT网络中
    def join_dht(self):
        """
        通过BOOTSTRAP_NODES引路从而加入DHT网络中
        """
        for address in Config.BOOTSTRAP_NODES:
            self.send_find_node(address)

    def rejoin_dht(self):
        '''
        每隔一段检查nodes是否没有了，没有则重新加入DHT网络
        '''
        if len(self.nodes) == 0:
            #print('nodes耗尽，从DHT网络获取nodes')
            self.join_dht()
        timer(Config.REJOIN_DHT_INTERVAL, self.rejoin_dht)


    def auto_send_find_node(self):
        '''
        从获取到的nodes中选出一个，并向其发送find_node请求
        '''
        while True:
            try:
                node = self.nodes.popleft()
                self.send_find_node((node.ip, node.port), node.nid)
            except IndexError:
                pass
            # 设置发送请求的时间间隔
            sleep(1.0 / Config.MAX_NODE_SIZE)

    def process_find_node_response(self, msg):
        nodes = decode_nodes(msg['r']['nodes'])
        for node in nodes:
            (nid, ip, port) = node
            #print('回复find_node')
            #print('回复来自' + node + '的find_node请求: ')
            if len(nid) != 20:
                print('node格式出错')
                continue
            if ip == self.bind_ip:
                print('find_node请求来自自身请求')
                continue
            n = KNode(nid, ip, port)
            # 将接收到的nodes加入的双端队列中
            print('收到node: {0} 加入双端队列中 from address {1}'.format(node, (ip, port)))
            self.nodes.append(n)
            #RedisClient2.set_keyinfo(nid, (ip, port))


# DHT服务类
class DHTServer(DHTClient):
    def __init__(self, bind_ip, bind_port, process_id):
        DHTClient.__init__(self, bind_ip, bind_port)
        # 客户端绑定ip和端口
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        # 进程id
        self.process_id = process_id
        # 线程池最大下载线程数
        self.pool = ThreadPoolExecutor(Config.DOWNLOAD_THREAD)
        # get_peers请求和announce_peer请求
        self.process_request_actions = {
            'get_peers': self.on_get_peers_request,
            'announce_peer': self.on_announce_peer_request,
        }

        # 定时器，定时重新加入DHT网络
        timer(Config.REJOIN_DHT_INTERVAL, self.rejoin_dht)
    def run(self):
        # 加入DHT网络
        self.rejoin_dht()
        # 监听套接字数据
        while True:
            #print('监听中....')
            # noinspection PyBroadException
            try:
                # 从socket上获取data和address
                (data, address) = self.ufd.recvfrom(65536)
                # 将数据解码
                msg = bdecode(data)
                # 监听信息，并回复
                self.on_message(msg, address)
            except Exception:
                pass

    # 处理request请求
    def on_message(self, msg, address):
        try:
            # 收到的信息为response
            if msg['y'] == 'r':
                # 收到对方发来的nodes
                if 'nodes' in msg['r']:
                    # 向对方发来的nodes发送find_node请求，进一步扩大路由表
                    self.process_find_node_response(msg)
            # 收到的信息为quest
            elif msg['y'] == 'q':
                try:
                    # 判断收到的信息是get_peers还是announce_peer请求，并回复相应报文
                    self.process_request_actions[msg['q']](msg, address)
                except KeyError:
                    # 回复出错，则装死。。
                    self.play_dead(msg, address)
        except KeyError:
            pass

    # 处理get_peers的request请求
    def on_get_peers_request(self, msg, address):
        #print('回复get_peers请求')
        print('收到get_peers请求 msg: {0} from address: {1}'.format(msg, address))
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

    def on_announce_peer_request(self, msg, address):
        #print('回复announce_peer请求')
        # noinspection PyBroadException
        print('收到announce_peer请求 msg: {0} from address: {1}'.format(msg, address))
        try:
            h = msg['a']['info_hash']
            token = msg['a']['token']
            if h[:2] == token:
                if 'implied_port ' in msg['a'] and msg['a']['implied_port '] != 0:
                    port = address[1]
                else:
                    port = msg['a']['port']
                # 下载metadata
                self.pool.submit(download_metadata, (address[0], port), h, self.process_id)
        except Exception:
            return
        finally:
            self.ok(msg, address)

    # 装死。。
    def play_dead(self, msg, address):
        try:
            tid = msg['t']
            msg = {
                't': tid,
                'y': 'e',
                'e': [202, 'Server Error']
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass
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

def _start_thread(offset):
    """
    启动线程

    :param offset: 端口偏移值
    """
    logger.info("DHT网络进程 运行 成功 ! {0} ->>>> {1}:{2}".format(offset,Config.BIND_IP,Config.BIND_PORT + offset))
    dht = DHTServer(Config.BIND_IP, Config.BIND_PORT + offset, offset)
    dht.start()
    dht.auto_send_find_node()
    # t = Thread(target=dht.auto_send_find_node)
    # t.start()
    # t.join()
    # dht.join()


def start_server():
    """
    多进程启动服务
    """
    processes = []
    # Config.MAX_PROCESSES
    for i in range(Config.MAX_PROCESSES):
        processes.append(Process(target=_start_thread, args=(i,)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()
