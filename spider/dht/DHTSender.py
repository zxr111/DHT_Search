import socket
from threading import Thread

from ..util.bcode import bencode

class DHTSender(Thread):
    '''
        DHT网络线程KRPC发送端
    '''
    def __init__(self, bind_ip, bind_port):
        Thread.__init__(self)
        # socket UDP
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # 绑定ip 和 port
        self.udp.bind((bind_ip, bind_port))

    # KRPC协议发送封装
    def send_krpc(self, msg, address):
        try:
            # krpc协议须将消息封装成bencode
            self.udp.sendto(bencode(msg), address)
        except Exception:
            print('krpc发送失败')

