import os
try:
    from qdrant_client import QdrantClient
except ImportError:
    QdrantClient = None

class QdrantConnection:
    def __init__(self):
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", "6333"))
        self.client = None

    def connect(self):
        if not QdrantClient:
            print("[QdrantConnection] qdrant-client not installed.")
            return None
        self.client = QdrantClient(host=self.host, port=self.port)
        return self.client

    def search_vectors(self, collection_name: str, query_vector: list, limit: int = 5):
        if not self.client:
            self.connect()
        if not self.client:
            return []
        return self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )
