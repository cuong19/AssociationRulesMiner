import psycopg2


class Postgres:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.conn = None
        self.cur = None

    def connect(self, dbname):
        try:
            self.conn = psycopg2.connect("dbname=" + str(dbname) +
                                         " user=" + str(self.user) + " password=" + str(self.password) +
                                         " host=" + str(self.host) + " port=" + str(self.port))
            self.cur = self.conn.cursor()
        except psycopg2.OperationalError:
            print("Cannot connect to the database " + str(dbname) + " at " + str(self.host) + ":" + str(self.port))
            raise ConnectionRefusedError

    def disconnect(self):
        self.cur.close()
        self.conn.close()

    def query(self, sql):
        self.cur.execute(sql)
        end_of_results = False
        records = []
        while end_of_results is False:
            record = self.cur.fetchone()
            if record is not None:
                records.append(record)
            else:
                end_of_results = True
        return records
