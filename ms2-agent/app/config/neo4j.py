from neo4j import GraphDatabase

from app.config.env import env

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            env.NEO4J_URI,
            auth=(env.NEO4J_USERNAME, env.NEO4J_PASSWORD),
        )
    return _driver


def connect_neo4j() -> None:
    """Test Neo4j connectivity on startup."""
    driver = get_driver()
    driver.verify_connectivity()
    print("[INFO] Neo4j connection established successfully.")


def close_neo4j() -> None:
    """Close the Neo4j driver on shutdown."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
