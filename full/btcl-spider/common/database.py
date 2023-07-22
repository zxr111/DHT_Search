#!/usr/bin/env python
# coding=utf-8

import redis
from .utils import get_logger
from config import Config

class RedisClient:

    def __init__(
        self, host=Config.REDIS_HOST, port=Config.REDIS_PORT, password=Config.REDIS_PASSWORD
    ):
        conn_pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password,
            max_connections=Config.REDIS_MAX_CONNECTION,
        )
        self.redis = redis.Redis(connection_pool=conn_pool)
        self.logger = get_logger("logger_redis")
        
    def set_keyinfo(self,infohash,metadata):
        """
        """    
        self.redis.set(infohash,metadata)

    def get_redis_byKey(self,key,count):
        """
        返回指定数量的磁力链接
        """
        return self.redis.srandmember(key, count)
    def getKeys(self):
        return self.redis.keys()

RedisClients = RedisClient()
RedisClient2 = RedisClient(2)
