import os


class Config(object):
    # 是否使用全部进程
    MAX_PROCESSES = 1# os.cpu_count() // 2 or os.cpu_count()

    # 初始化DHT网络节点
    BOOTSTRAP_NODES = (
        ('router.bittorrent.com', 6881),
        ('dht.transmissionbt.com', 6881),
        ('router.utorrent.com', 6881)
    )

    # 掉线后重新加入DHT网络的时间间隔
    REJOIN_DHT_INTERVAL = 3
    # 绑定ip为默认路由
    BIND_IP = '0.0.0.0'
    # 绑定端口
    BIND_PORT = 12248
    # 双端队列最大节点
    MAX_NODE_SIZE = int(os.environ.get('MAX_NODE_SIZE', '5000'))


if __name__ == "__main__":
    print(Config.MAX_NODE_SIZE)