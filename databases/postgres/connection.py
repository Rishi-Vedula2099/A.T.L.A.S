import os
import psycopg2
from psycopg2.extras import RealDictCursor

class PostgresConnection:
    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.user = os.getenv("POSTGRES_USER", "atlas_admin")
        self.password = os.getenv("POSTGRES_PASSWORD", "atlas_password_9921")
        self.db = os.getenv("POSTGRES_DB", "atlas_db")
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.db
        )
        return self.conn

    def execute_query(self, query: str, params: tuple = None):
        if not self.conn or self.conn.closed:
            self.connect()
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            self.conn.commit()
            try:
                return cur.fetchall()
            except psycopg2.ProgrammingError:
                return None

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
