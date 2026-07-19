from neo4j.debug import watch
from neo4j import GraphDatabase

watch("neo4j")

driver = GraphDatabase.driver(
    "neo4j+s://47d9936b.databases.neo4j.io",
    auth=("47d9936b", "YOUR_PASSWORD")
)

driver.verify_connectivity()