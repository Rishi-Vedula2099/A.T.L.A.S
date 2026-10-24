from databases.neo4j.connection import Neo4jConnection

class GraphMemoryService:
    def __init__(self):
        self.db = Neo4jConnection()

    def add_relationship(self, user_name: str, technology: str, relationship: str):
        cypher = """
            MERGE (u:User {name: $user})
            MERGE (t:Technology {name: $tech})
            MERGE (u)-[r:%s]->(t)
            SET r.timestamp = timestamp()
            RETURN u, t;
        """ % relationship
        
        self.db.query(cypher, {"user": user_name, "tech": technology})
        print(f"[GraphMemory] Linked {user_name} -> [{relationship}] -> {technology}")
