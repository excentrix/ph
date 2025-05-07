from neo4j import GraphDatabase
from typing import Dict, Any, List, Optional
from core.config import settings

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
        
    def query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return the results."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    async def async_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Asynchronous version of query method (using async_)."""
        async with self.driver.async_session() as session:
            result = await session.run(query, parameters or {})
            return [record.data() async for record in result]

# Singleton instance
neo4j_client = Neo4jClient(
    settings.NEO4J_URI,
    settings.NEO4J_USER,
    settings.NEO4J_PASSWORD
)
