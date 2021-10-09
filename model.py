from config import JsonConfig


class Model:

    def __init__(self, path):
        self.config = JsonConfig(path)
        self.data = None

    def save(self, data):
        self.data = data
        self.config.write_file(data)

    def load(self):
        self.data = self.config.read_file()
        return self.data
