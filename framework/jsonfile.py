# Stdlib
import json


class JsonFile:
    def __init__(self, filename: str):
        self.filename = filename
        with open(filename) as f:
            self.data = json.load(f)

    def __setitem__(self, key, value):
        self.data[key] = value
        with open(self.filename, "w") as f:
            json.dump(self.data, f)

    def __getitem__(self, item):
        return self.data[item]

    def __eq__(self, other):
        return self.data == other
