from src.common.yaml import Yaml
from src.common.postgres import Postgres
from src.common.path import Path
from src.association_rules.transaction import Transaction

if __name__ == "__main__":
    path = Path(__file__)
    config = None
    try:
        config = Yaml(path.get_absolute_path("config.yml")).content
    except FileNotFoundError:
        print("Cannot find config.yml!")

    postgres = Postgres(host=config['source']['host'], port=config['source']['port'],
                        user=config['source']['user'], password=config['source']['password'])
    try:
        postgres.connect(dbname=config['source']['dbname'])
    except ConnectionRefusedError:
        pass

    records = postgres.query("SELECT DISTINCT " +
                             str(config['source']['transaction_column']) + ", " + str(config['source']['item_column']) +
                             " FROM " + str(config['source']['table']) +
                             " ORDER BY " + str(config['source']['transaction_column']))

    transactions = Transaction.list_maker(records)

    for transaction in transactions:
        print(transaction)

    postgres.disconnect()
