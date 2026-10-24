import os
import redis

class RedisConnection:
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.client = None

    def connect(self):
        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            decode_responses=True
        )
        return self.client

    def set_value(self, key: str, value: str, expiry_seconds: int = None):
        if not self.client:
            self.connect()
        self.client.set(key, value, ex=expiry_seconds)

    def get_value(self, key: str) -> str:
        if not self.client:
            self.connect()
        return self.client.get(key)
