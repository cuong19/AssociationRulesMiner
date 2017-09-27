from src.common.yaml import Yaml
from src.common.postgres import Postgres, PostgresQueryError
from src.common.path import Path
from src.association_rules.transaction import Transaction
from src.association_rules.fpgrowth import FPGrowth
from src.common.neo4j_driver import Neo4jDriver
from src.custom import CustomProcess


def get_config(path, filename):
    """
    Get the config file
    :param path: usually Path(__file__) to get the path of the current app
    :param filename: name of the config file
    :return: The config variable if succeeded
    """
    try:
        return Yaml(path.get_absolute_path(filename)).content
    except FileNotFoundError:
        return None


def get_transactions_list(config):
    """
    Query from Postgres to get the transactions list
    :param config: the configurations
    :return: The transactions list if succeeded
    """
    postgres = Postgres(host=config['source']['host'], port=config['source']['port'],
                        user=config['source']['user'], password=config['source']['password'])
    print("Connecting to Postgres...")
    try:
        postgres.connect(dbname=config['source']['dbname'])
        print("OK")
    except ConnectionRefusedError:
        print("Failed")
        return None

    print("Querying from Postgres...")
    try:
        records = postgres.query("SELECT DISTINCT " +
                                 str(config['source']['transaction_column']) + ", " +
                                 str(config['source']['item_column']) +
                                 " FROM " + str(config['source']['table']) +
                                 " ORDER BY " + str(config['source']['transaction_column']))
        print("OK")
    except PostgresQueryError:
        return None
    finally:
        print("Disconnecting from Postgres...")
        postgres.disconnect()
        print("OK")

    print("Making transactions list...")
    transactions = Transaction.list_maker(records)
    print("OK")
    return transactions


def split_transactions(transactions):
    """
    Split transactions into 80% to learn and 20% to test
    :param transactions: The whole transactions list
    :return: The transactions list to be learnt, the transactions list to be tested
    """
    i = int(len(transactions) * 0.8)
    transactions_to_learn = transactions[:i]
    print(str(len(transactions_to_learn)) + " transactions will be used to learn.")
    transactions_to_test = transactions[i:]
    print(str(len(transactions_to_test)) + " transactions will be used to test.")
    return transactions_to_learn, transactions_to_test


def fpgrowth_mine(transactions, config):
    """
    Mine the transactions using FP-growth
    :param transactions: The transactions in the form of a list with each element being a transaction containing items
    :param config: The configurations
    :return: The mined fpgrowth instance
    """
    print("Mining using FP-growth...")
    fpgrowth = FPGrowth(transactions, config['mining_var']['support'],
                        config['mining_var']['min_set'], config['mining_var']['max_set'])
    print("OK")
    print(str(fpgrowth.no_rules) + " rules created.")
    return fpgrowth


def save_rules_to_neo4j(fpgrowth, config):
    """
    Save the rules to Neo4j
    :param fpgrowth: The mined fpgrowth instance
    :param config: The configurations
    :return: None in case of failure
    """
    neo4j_driver = Neo4jDriver(host=config['target']['host'], port=config['target']['port'],
                               user=config['target']['user'], password=config['target']['password'])

    print("Connecting to Neo4j database...")
    try:
        neo4j_driver.connect()
        print("OK")
    except ConnectionError:
        print("Failed!")
        return None

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


if __name__ == "__main__":
    # Parse the config file
    conf = get_config(Path(__file__), "config.yml")

    if conf is not None:

        trans = get_transactions_list(conf)
        CustomProcess.transaction_process(trans)

        if trans is not None:
            trans_to_learn, trans_to_test = split_transactions(trans)
            fpgrowth_mined = fpgrowth_mine(trans_to_learn, conf)

            if conf['preferences']['save_to_target']:
                save_rules_to_neo4j(fpgrowth_mined, conf)
            if conf['preferences']['print_rules_mine']:
                fpgrowth_mined.pretty_print()
