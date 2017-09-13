import yaml


class Yaml:
    def __init__(self, file):
        self.file = file
        self.content = None
        self.parse()

    def parse(self):
        with open(self.file) as f:
            read_data = f.read()
        self.content = yaml.load(read_data)
