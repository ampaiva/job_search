import json


class WordsList:
    def __init__(self):
        with open('words.json', 'r') as file:
            self._data = json.load(file)

    def words(self, category):
        return self._data[category]
