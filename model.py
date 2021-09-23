import sys

from config import JsonConfig

MODEL_SAVE_PATH = sys.path[0] + "/{0}_data.json"


class Model:

    def __init__(self, game):
        self.game = game
        self.config = JsonConfig(MODEL_SAVE_PATH.format(game))
        self.data = None

    def save(self, data):
        self.data = data
        self.config.write_file(data)

    def load(self):
        self.data = self.config.read_file()
        return self.data