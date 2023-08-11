import os
import neo4j

NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
NEO4J_LINK = os.environ.get("NEO4J_LINK")


def connect_to_auradb():
    uri = NEO4J_LINK
    username = "neo4j"
    password = NEO4J_PASSWORD

    driver = neo4j.GraphDatabase.driver(uri, auth=(username, password))
    return driver


driver = connect_to_auradb()


def check_auradb_connection():
    print("AuraDB Connected with the id of", driver.get_server_info().connection_id)


def remove_underscore(input_string):
    return input_string.replace("_", " ")


class Neo4jNode:
    def __init__(self, node_label, node_type, name, content, node_id):
        self.node_label: list = node_label
        self.node_type: str = node_type
        self.name: str = name
        self.content: str = content
        self.id: str = node_id

    def __str__(self):
        return f"<Node Type: {self.node_type}, Label: {self.node_label}, Name: {self.name}, Content: {self.content}, ID: {self.id}>"

    def __repr__(self):
        return f"<Node Type: {self.node_type}, Label: {self.node_label}, Name: {self.name}, Content: {self.content}, ID: {self.id}>"


def extract_node(node_item):
    try:
        node_labels = list(node_item.labels)
        if "EVENT" in node_labels:
            content = remove_underscore(
                (
                    node_item["name"] + ": " + node_item["summary"]
                    if node_item["summary"] is not None
                    else node_item["name"]
                )
            )
            return Neo4jNode(
                node_labels, "EVENT", node_item["name"], content, node_item["id"]
            )
        elif "IDEA" in node_labels:
            content = remove_underscore(node_item["name"])
            return Neo4jNode(
                node_labels, "IDEA", node_item["name"], content, node_item["id"]
            )
        elif "FACT" in node_labels:
            content = remove_underscore(node_item["name"])
            return Neo4jNode(
                node_labels, "FACT", node_item["name"], content, node_item["id"]
            )
        else:
            content = remove_underscore(node_item["name"])
            return Neo4jNode(
                node_labels, "ENTITY", node_item["name"], content, node_item["id"]
            )
    except Exception as e:
        print(
            f"🔥 utils/neo4j/common/extract_node: [extract_node] failed 🔥",
            e,
        )


def find_shortest_path_between_two_entity(entity_1_name: str, entity_2_name: str):
    try:
        records, summary, keys = driver.execute_query(
            f"""
            MATCH (n {{name: "{entity_1_name}"}}), (m {{name: "{entity_2_name}"}})
            MATCH path = shortestPath((n)-[*]-(m))
            RETURN nodes(path), relationships(path)
            """,
            database_="neo4j",
        )

        items = records[0]
        nodes = items[0]
        relationships = items[1]
        extracted_informations = []

        for node_item in nodes:
            dict_node_item = extract_node(node_item)
            extracted_informations.append(dict_node_item)

        print("■■■■■■■■■[Graph-Extracted]■■■■■■■■■")
        print("nodes count: ", len(nodes), "relationships count", len(relationships))
        print(extracted_informations)

        return extracted_informations
    except Exception as e:
        print(
            f"🔥 utils/neo4j/common/find_shortest_path_between_two_entity: [find_shortest_path_between_two_entity] failed 🔥",
            e,
        )


def find_shortest_path_between_two_entity(entity_1_name: str, entity_2_name: str):
    try:
        records, summary, keys = driver.execute_query(
            f"""
            MATCH (n {{name: "{entity_1_name}"}}), (m {{name: "{entity_2_name}"}})
            MATCH path = shortestPath((n)-[*]-(m))
            RETURN nodes(path), relationships(path)
            """,
            database_="neo4j",
        )

        items = records[0]
        nodes = items[0]
        relationships = items[1]
        extracted_informations = []

        for node_item in nodes:
            dict_node_item = extract_node(node_item)
            extracted_informations.append(dict_node_item)

        print("■■■■■■■■■[Graph-Extracted]■■■■■■■■■")
        print("nodes count: ", len(nodes), "relationships count", len(relationships))
        print(extracted_informations)

        return extracted_informations
    except Exception as e:
        print(
            f"🔥 utils/neo4j/common/find_shortest_path_between_two_entity: [find_shortest_path_between_two_entity] failed 🔥",
            e,
        )


def find_multiple_pathes_between_two_entity(
    entity_1_name: str, entity_2_name: str, count: int
):
    try:
        records, summary, keys = driver.execute_query(
            f"""
            MATCH p=allShortestPaths((start {{name: "{entity_1_name}"}})-[*1..10]-(end {{name: "{entity_2_name}"}}))
            WITH p, length(p) AS pathLength
            ORDER BY pathLength
            LIMIT {count}
            UNWIND nodes(p) AS node
            WITH COLLECT(DISTINCT node) AS nodes
            RETURN nodes;
            """,
            database_="neo4j",
        )

        extracted_informations = []

        for node_item in records[0]["nodes"]:
            dict_node_item = extract_node(node_item)
            extracted_informations.append(dict_node_item)

        # print("■■■■■■■■■[Multiple-Path-Graph-Extracted]■■■■■■■■■")
        # print("nodes count: ", len(extracted_informations))

        return extracted_informations
    except Exception as e:
        print(
            f"🔥 utils/neo4j/common/find_multiple_pathes_between_two_entity: [find_multiple_pathes_between_two_entity] failed 🔥",
            e,
        )


async def find_path_to_nearest_event_entity(entity_name: str, count: int):
    try:
        records, summary, keys = driver.execute_query(
            f"""
            MATCH (start {{name: "{entity_name}"}})
            MATCH (end:EVENT)
            WHERE start <> end
            MATCH p=shortestPath((start)-[*1..10]-(end))
            WITH length(p) as calculated_distance, p
            WITH p, REDUCE(s = 0, rel IN relationships(p) | s + rel.distance) as total_distance
            ORDER BY total_distance
            LIMIT {count}
            RETURN nodes(p), relationships(p)
            """,
            database_="neo4j",
        )

        items = records[0]
        nodes = items[0]
        extracted_informations = []

        for node_item in nodes:
            dict_node_item = extract_node(node_item)
            extracted_informations.append(dict_node_item)

        # print("■■■■■■■■■[Nearest-Event-Extracted]■■■■■■■■■")
        # print("nodes count: ", len(extracted_informations))

        return extracted_informations
    except Exception as e:
        print(
            f"🔥 utils/neo4j/common/find_path_to_nearest_event_entity: [find_path_to_nearest_event_entity] failed 🔥",
            e,
        )
