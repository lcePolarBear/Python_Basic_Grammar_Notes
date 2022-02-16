import redis


class RedisConnet(object):
    def __init__(self) -> None:
        """
        初始化 redis 数据库连接
        """
        self.r = redis.StrictRedis(host='192.168.102.242', port=6379, db=0, decode_responses=True)
    def redisget(self, id):
        """
        通过 redis key 获取并返回 redis value
        """
        return self.r.get(id)
    def redisset(self, id, imageUrl):
        """
        通过 redis key 和 redis value 写入 redis 缓存
        """
        return self.r.set(id, imageUrl)