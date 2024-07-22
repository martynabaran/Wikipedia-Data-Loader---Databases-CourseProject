import sys
from neo4j import GraphDatabase
import time

# Neo4j connection details
#User need to change for his uri, username and password
uri = ""
username = "neo4j"
password = ""

# Define your queries
queries = {
    0: "CREATE INDEX loading_index FOR (n:Title) ON (n.name);",
    1: "MATCH (c:Title{{name: \"{}\"}})-[:HAS_SUBCATEGORY]->(s) RETURN s;",
    2: "MATCH (c:Title {{name: \"{}\"}})-[r:HAS_SUBCATEGORY]->(s:Title) RETURN count(r) As numberOfChildren",
    3: "MATCH (c:Title {{name: \"{}\"}})-[:HAS_SUBCATEGORY]-{{2}}(s:Title) RETURN DISTINCT s",
    4: "MATCH (c:Title)-[:HAS_SUBCATEGORY]->(s:Title{{name: \"{}\"}}) RETURN c",
    5: "MATCH (c:Title)-[r:HAS_SUBCATEGORY]->(s:Title {{name: \"{}\"}}) RETURN count(r) As numberOfParents",
    6: "MATCH (c:Title)-[:HAS_SUBCATEGORY]-{{2}}(s:Title{{name: \"{}\"}}) RETURN DISTINCT c",
    7: "MATCH (c:Title) RETURN count(c) as totalNum",
    8: "MATCH (c:Title) WHERE NOT EXISTS( ()-[:HAS_SUBCATEGORY]->(c:Title)) Return c as RootNodes",
    9: "CALL{ MATCH (parent:Title)-[:HAS_SUBCATEGORY]->(child:Title) RETURN parent, COUNT(child) AS childCount ORDER BY childCount DESC LIMIT 1} MATCH (c:Title)-[:HAS_SUBCATEGORY]->(s:Title) WITH c,childCount, COUNT(s) AS actualChildCount WHERE actualChildCount = childCount RETURN c,childCount;",
    10: "CALL{ MATCH (parent:Title)-[:HAS_SUBCATEGORY]->(child:Title) RETURN parent, COUNT(child) AS childCount ORDER BY childCount LIMIT 1 } MATCH (c:Title)-[:HAS_SUBCATEGORY]->(s:Title) WITH c,childCount, COUNT(s) AS actualChildCount WHERE actualChildCount = childCount RETURN c,childCount;",
    11: "MATCH (c:Title) WHERE c.name = \"{}\" SET c.name= \"{}\"",
    12: "MATCH path = (startNode:Title)-[:HAS_SUBCATEGORY*]->(endNode:Title) WHERE startNode.name = \"{}\" AND endNode.name = \"{}\" UNWIND path AS all_nodes RETURN all_nodes",
    13: "LOAD CSV FROM 'file:///taxonomy_iw.csv' AS row CALL { WITH row MERGE (c:Title {name :row[0]}) MERGE (s:Title {name:row[1]}) MERGE (c)-[:HAS_SUBCATEGORY]->(s)} IN TRANSACTIONS;",
    14: "server status"
}


def run_query(session, goal_number, args):
    if goal_number in ["index", "loading"]:
        query = queries.get(goal_number)
        start_time = time.time()
        result = session.run(query)
        end_time = time.time()


    else:
        query = queries.get(int(goal_number))
        if not query:
            print("Invalid goal number")
            return
        if args:
            query = query.format(*args)
        print(f"Executed query: {query}")
        if goal_number != "11":
            print("Query result:")
        start_time = time.time()
        result = session.run(query)
        end_time = time.time()
        if int(goal_number) == 12:
            for path in result:
                print(*path.data()["all_nodes"])
        if int(goal_number) in [1,3]:
            for record in result: 
                print(record.data()['s']['name'])
        if int(goal_number) in [12,4,6,9]:
            for record in result:    
                print(record.data()['c']['name'])
        if int(goal_number) in [2,5,7]:
            for record in result:    
                print(record.data())
        if int(goal_number) in [8]:
            for record in result:    
                print(record.data()["RootNodes"])
        if int(goal_number) in [10]:  
            for record in result:    
                print(f"{record.data()['c']['name']} (childCount = {record.data()['childCount']})")      
        if int(goal_number) in [11]:
            print(f"Name changed from \"{args[0]}\" to \"{args[1]}\"")

    print(f"Execution time: {end_time-start_time}")
    

       

def main(argv):
    if len(argv) < 2:
        print("Usage: dbcli <goal_number> [args...]")
        return

    goal_number = argv[1]
    args = argv[2:]
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        with driver.session() as session:
            run_query(session, goal_number, args)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    main(sys.argv)
