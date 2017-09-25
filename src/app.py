from src.common.yaml import Yaml
from src.common.postgres import Postgres
from src.common.path import Path
from src.association_rules.transaction import Transaction
from src.association_rules.fpgrowth import FPGrowth
from src.common.neo4j_driver import Neo4jDriver
from src.custom import CustomProcess

if __name__ == "__main__":
    path = Path(__file__)
    config = None
    try:
        config = Yaml(path.get_absolute_path("config.yml")).content
    except FileNotFoundError:
        print("Cannot find config.yml!")

    postgres = Postgres(host=config['source']['host'], port=config['source']['port'],
                        user=config['source']['user'], password=config['source']['password'])
    print("Connecting to Postgres...")
    try:
        postgres.connect(dbname=config['source']['dbname'])
        print("OK")
    except ConnectionRefusedError:
        postgres = None
        print("Failed")

    if postgres is not None:
        print("Querying from Postgres...")
        records = postgres.query("SELECT DISTINCT " +
                                 str(config['source']['transaction_column']) + ", " +
                                 str(config['source']['item_column']) +
                                 " FROM " + str(config['source']['table']) +
                                 " ORDER BY " + str(config['source']['transaction_column']))
        print("OK")
        print("Disconnecting from Postgres...")
        postgres.disconnect()
        print("OK")
        print("Making transactions list...")
        transactions = Transaction.list_maker(records)
        CustomProcess.transaction_process(transactions)
        print("OK")
        print("Mining using FP-growth...")
        fpgrowth = FPGrowth(transactions, config['mining_var']['support'],
                            config['mining_var']['min_set'], config['mining_var']['max_set'])
        print("OK")
        print("Rules created")
        print(fpgrowth.no_rules)

        if config['target']['use']:
            neo4j_driver = Neo4jDriver(host=config['target']['host'], port=config['target']['port'],
                                       user=config['target']['user'], password=config['target']['password'])

            print("Connecting to Neo4j database...")
            try:
                neo4j_driver.connect()
                print("OK")
            except ConnectionError:
                neo4j_driver = None
                print("Failed!")

            i = 0
            if neo4j_driver is not None:

                print("Writing rules to Neo4j database...")
                i = 0
                for rule in fpgrowth.rules:
                    antecedents_str = ""
                    for antecedent in rule.antecedents:
                        antecedents_str += "'" + str(antecedent) + "',"

                    antecedents_str = antecedents_str[:-1]

                    # Create a new set if not existed in database
                    neo4j_driver.query("MERGE (s:ItemSet {name: {name}})",
                                       {"name": antecedents_str})
                    for antecedent in rule.antecedents:
                        # Insert node :Item if not existed in database
                        neo4j_driver.query("MERGE (i:Item {name: {name}})", {"name": str(antecedent)})
                        # Insert relation between the node and the set
                        neo4j_driver.query("MATCH (i:Item),(s:ItemSet) WHERE i.name = {iname} AND s.name = {sname} "
                                           "MERGE (i)-[r:OCCURS_IN]->(s) RETURN r",
                                           {"iname": str(antecedent), "sname": antecedents_str})
                    # Insert node :Item using consequent item if not existed in database
                    neo4j_driver.query("MERGE (i:Item {name: {name}})", {"name": str(rule.consequent)})

                    # Create the relation between the node and the set with attributes:
                    # Consequent, Confidence, Lift
                    neo4j_driver.query("MATCH (i:Item),(s:ItemSet) WHERE i.name = {iname} AND s.name = {sname}"
                                       "MERGE (i)<-"
                                       "[r:OCCURS_WITH { support:{support}, confidence:{confidence}, lift:{lift} }]"
                                       "-(s)"
                                       " RETURN r",
                                       {"iname": str(rule.consequent), "sname": antecedents_str,
                                        "support": rule.support, "confidence": rule.confidence, "lift": rule.lift})
                    i += 1
                    print(str(i) + ". [" + antecedents_str + "] -> '" + str(rule.consequent) + "'")

                neo4j_driver.disconnect()
        else:
            fpgrowth.pretty_print()
