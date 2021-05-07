import sys


class TranspositionTable:
    table = {}

    size = 0

    UPPER_BOUND = 1
    EXACT = 0
    LOWER_BOUND = -1

    def __init__(self, table):
        self.table = table

    def addEntry(self, key, score, depth, flag):
        # Max size 64MB
        # if sys.getsizeof(self.table) >= 67108864:
        if self.size >= 1048576:
            # print("Transposition Table Max Size, Tamanho {}".format(self.size))
            return

        self.table[key] = {"score": score, "depth": depth, "flag": flag}

        self.size += 1

    def removeEntry(self, key):
        return self.table.pop(key)

    def resetTable(self):
        self.table = {}

    def getEntry(self, key):
        if key in self.table:
            return self.table[key]

        return None
