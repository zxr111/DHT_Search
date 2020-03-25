import redis
from ..config import Config
from ..util.common import get_logger


class RedisClient(object):
    def __init__(self,
        db, host=Config.REDIS_HOST, port=Config.REDIS_PORT, password=Config.REDIS_PWD
    ):
        # 初始化redis信息
        conn_pool = redis.ConnectionPool(
            db=db,
            host=host,
            port=port,
            password=password,
            max_connections=Config.REDIS_MAX_CONNECTION,
        )
        self.redis = redis.Redis(connection_pool=conn_pool)
        self.logger = get_logger("logger_redis_{}".format(port))
    # 将接收到的node存入redis
    def add_node(self, node):
        try:
            self.redis.sadd('nodes', node.nid, node.ip, node.port)
        except KeyError:
            pass