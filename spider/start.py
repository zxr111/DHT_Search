from multiprocessing import Process

from .config import Config
from .dht.DHTServer import DHTServer
from .util.common import get_logger

logger = get_logger("logger_dht_main")

# 启动多进程
def start_processes(id):
    logger.info("DHT网络进程{0}运行成功 !!! 绑定地址 ------> {1}:{2}".format(id, Config.BIND_IP, Config.BIND_PORT + id))
    dht_server = DHTServer(Config.BIND_IP, Config.BIND_PORT + id, id)
    dht_server.start()
    dht_server.auto_send_find_node()

# 启动多进程服务
def start_server():
    processes = []
    for id in range(Config.MAX_PROCESSES):
        processes.append(Process(target=start_processes, args=(id,)))

    for p in processes:
        p.start()

    for p in processes:
        p.join()
