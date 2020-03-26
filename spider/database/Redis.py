import redis
from ..config import Config
from ..util.common import get_logger


class RedisClient:

    def __init__(
            self, db, host=Config.REDIS_HOST, port=Config.REDIS_PORT, password=Config.REDIS_PASSWORD
    ):
        conn_pool = redis.ConnectionPool(
            db=db,
            host=host,
            port=port,
            password=password,
            max_connections=Config.REDIS_MAX_CONNECTION,
        )
        self.redis = redis.Redis(connection_pool=conn_pool)
        self.logger = get_logger("logger_redis_{}".format(port))

    def add_peer(self, infohash, address):
        """
        新增磁力peer信息
        """
        self.redis.sadd('peer', str(infohash) + ':' + address[0] + ':' + str(address[1]))
        # if (self.redis.exists(infohash) == False):
        #     self.redis.sadd('peer',str(infohash)+':'+address[0]+':'+str(address[1]))
        # else:
        #     self.logger.info("该种子已存在:infohash>{0}".format(infohash))

    def set_keyinfo(self, infohash, metadata):
        """
        """
        self.redis.set(infohash, metadata)

    def get_redis_byKey(self, key, count):
        """
        返回指定数量的磁力链接
        """
        return self.redis.srandmember(key, count)

    def getKeys(self):
        return self.redis.keys()

    def getValue(self, key):
        return self.redis.get(key)

    def deleteByKey(self, key):
        self.redis.delete(key)

    def isKeyExis(self, key):
        return self.redis.exists(key)


RedisClients = RedisClient(0)
RedisClients1 = RedisClient(1)
RedisClient2 = RedisClient(2)