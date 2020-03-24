class NODE(object):
    '''
        nid, ip, port 组成的三元组
        DHT网络路由表单元
    '''
    def __init__(self, nid, ip, port):
        self.nid = nid
        self.ip = ip
        self.port = port