from src.common.yaml import Yaml
from src.common.postgres import Postgres
from src.common.path import Path
from src.association_rules.transaction import Transaction
from src.association_rules.fpgrowth import FPGrowth

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
        print("OK")
        print("Mining using FP-growth...")
        fpgrowth = FPGrowth(transactions, 0.1, 1, 5)
        print("OK")
        print("Rules created:")
        fpgrowth.pretty_print()
        # print(fpgrowth.total_lift/fpgrowth.no_rules)
