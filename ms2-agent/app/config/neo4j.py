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
    try:
        driver = get_driver()

        # Temporary debug
        print("=" * 60)
        print("NEO4J URI      :", env.NEO4J_URI)
        print("NEO4J DATABASE :", env.NEO4J_DATABASE)
        print("NEO4J USER     :", env.NEO4J_USERNAME)
        print("=" * 60)

        driver.verify_connectivity()

        with driver.session(database=env.NEO4J_DATABASE) as session:
            print("DB INFO:", session.run("CALL db.info()").single().data())

        print("[INFO] Neo4j connection established successfully.")

    except Exception as e:
        print(f"[WARNING] Neo4j connectivity check failed: {e}")
        print("[WARNING] ms2-agent will continue running, but Neo4j operations may fail.")


def close_neo4j() -> None:
    """Close the Neo4j driver on shutdown."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None