from neo4j.v1 import GraphDatabase, basic_auth


class Neo4jDriver:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.driver = None
        self.session = None

    def connect(self):
        self.driver = GraphDatabase.driver("bolt://" + str(self.host) + ":" + str(self.port),
                                      auth=basic_auth(self.user, self.password))
        self.session = self.driver.session()

    def disconnect(self):
        self.session.close()

    def query(self, query, params):
        self.session.run(query, params)