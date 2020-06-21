import redis

class Redis:
  def __init__(self):
    self.pool = redis.ConnectionPool(host="localhost",port=6379,decode_responses=True)
  def getConnect(self):
    return redis.Redis(connection_pool=self.pool)