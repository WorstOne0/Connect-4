import sys

# https://web.archive.org/web/20071031100051/http://www.brucemo.com/compchess/programming/hashing.htm


class TranspositionTable:
    # "Hash" Table
    table = {}

    size = 0

    UPPER_BOUND = 1
    EXACT = 0
    LOWER_BOUND = -1

    def __init__(self, table):
        # Initialize the Table
        self.table = table

    # Add to the table
    def addEntry(self, key, score, depth, flag):
        # Max size 64MB, approximate
        if self.size >= 1048576:
            return

        # Add the board to the table - the board is just a number with 49bytes
        self.table[key] = {"score": score, "depth": depth, "flag": flag}

        self.size += 1

    # Get a entry
    def getEntry(self, key):
        if key in self.table:
            return self.table[key]

        return None

    def removeEntry(self, key):
        return self.table.pop(key)

    def resetTable(self):
        self.table = {}
