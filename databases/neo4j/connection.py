import os
try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

class Neo4jConnection:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "atlas_neo4j_password_9921")
        self.driver = None

    def connect(self):
        if not GraphDatabase:
            print("[Neo4jConnection] neo4j library not installed.")
            return None
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self.driver

    def query(self, cypher: str, parameters: dict = None):
        if not self.driver:
            self.connect()
        if not self.driver:
            return None
        with self.driver.session() as session:
            result = session.run(cypher, parameters)
            return [record.data() for record in result]

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None
