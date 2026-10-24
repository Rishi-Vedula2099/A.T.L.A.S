from databases.postgres.connection import PostgresConnection
from databases.redis.connection import RedisConnection

class MemoryService:
    def __init__(self):
        self.db = PostgresConnection()
        self.cache = RedisConnection()

    def store_interaction(self, session_id: str, sender: str, text: str):
        query = """
            INSERT INTO session_messages (session_id, role, content) 
            VALUES (%s, %s, %s);
        """
        self.db.execute_query(query, (session_id, sender, text))
        
        # Cache message locally in Redis for 10-turn window
        self.cache.set_value(f"session:{session_id}:latest", text, expiry_seconds=3600)
        print(f"[MemoryService] Stored interaction for session: {session_id}")
