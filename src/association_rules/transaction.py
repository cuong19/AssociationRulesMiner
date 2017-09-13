class Transaction:
    def __init__(self, identifier=None, items=None):
        self.identifier = identifier if identifier is not None else 'anonymous'
        self.items = items if items is not None else []

    @staticmethod
    def list_maker(records):
        transactions = []
        current_transaction = Transaction()
        for record in records:
            # print(record)
            if current_transaction.identifier != record[0]:
                if current_transaction.items != []:
                    transactions.append(current_transaction.items)
                current_transaction = Transaction(record[0])
                # print(current_transaction.identifier)
            current_transaction.items.append(record[1])
        return transactions
