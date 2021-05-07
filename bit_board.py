import pygame
import numpy as np

from __init__ import GameConstants


# https://github.com/denkspuren/BitboardC4/blob/master/BitboardDesign.md


class Board:
    rows = 0
    columns = 0

    bitBoard = [None, None]
    rowsAvaliable = [0, 7, 14, 21, 28, 35, 42]
    topRows = [6, 13, 20, 27, 34, 41, 48]

    moves = []
    playedMoves = 0

    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns

    def insertPosition(self, moves):
        player = 0

        for move in moves:
            if self.isColumnMoveAllowed(int(move)):
                self.addChip(player, int(move))

                player = 1 if player == 0 else 0

        return player

    def addChip(self, player, column):
        move = int(1 << self.rowsAvaliable[column])
        self.rowsAvaliable[column] += 1

        if self.bitBoard[player] == None:
            self.bitBoard[player] = move
        else:
            self.bitBoard[player] ^= move

        self.moves.append(column)
        self.playedMoves += 1

    def removeChip(self, player, column):
        column = self.moves.pop()
        self.playedMoves -= 1

        self.rowsAvaliable[column] -= 1
        move = int(1 << self.rowsAvaliable[column])

        self.bitBoard[player] ^= move

    def isColumnMoveAllowed(self, column):
        if self.rowsAvaliable[column] == self.topRows[column]:
            return False

        return True

    def checkObjective(self, player):
        if self.bitBoard[player] == None:
            return

        if (
            self.bitBoard[player]
            & (self.bitBoard[player] >> 6)
            & (self.bitBoard[player] >> 12)
            & (self.bitBoard[player] >> 18)
            != 0
        ):
            return True  # diagonal \
        if (
            self.bitBoard[player]
            & (self.bitBoard[player] >> 8)
            & (self.bitBoard[player] >> 16)
            & (self.bitBoard[player] >> 24)
            != 0
        ):
            return True  # diagonal /
        if (
            self.bitBoard[player]
            & (self.bitBoard[player] >> 7)
            & (self.bitBoard[player] >> 14)
            & (self.bitBoard[player] >> 21)
            != 0
        ):
            return True  # horizontal
        if (
            self.bitBoard[player]
            & (self.bitBoard[player] >> 1)
            & (self.bitBoard[player] >> 2)
            & (self.bitBoard[player] >> 3)
            != 0
        ):
            return True  # vertical

        return False

    def isMovesLeft(self):
        return False if self.playedMoves == self.rows * self.columns else True

    def bitPosition(self, player, row, column):
        if self.bitBoard[player] == None:
            return

        bitBoardString = self.getBinaryString(player)

        grid = [
            [43, 44, 45, 46, 47, 48],
            [36, 37, 38, 39, 40, 41],
            [29, 30, 31, 32, 33, 34],
            [22, 23, 24, 25, 26, 27],
            [15, 16, 17, 18, 19, 20],
            [8, 9, 10, 11, 12, 13],
            [1, 2, 3, 4, 5, 6],
        ]

        return bitBoardString[grid[column][row]]

    def getBinaryString(self, player, boardSize=49):
        if self.bitBoard[player] != None:
            return format(self.bitBoard[player], "b").zfill(boardSize)

    def printBitBoard(self, player):
        if self.bitBoard[player] == None:
            return

        bitBoardString = self.getBinaryString(player)

        row = self.rows + 1
        for i in range(0, row, 1):
            print(
                bitBoardString[row * 6 + i],
                bitBoardString[row * 5 + i],
                bitBoardString[row * 4 + i],
                bitBoardString[row * 3 + i],
                bitBoardString[row * 2 + i],
                bitBoardString[row * 1 + i],
                bitBoardString[row * 0 + i],
            )

    def draw(self, screen, game):
        rects = []

        rects = [screen.fill(GameConstants.ColorBackground)]

        gridWidth = self.columns
        gridHeight = self.rows

        for row in range(gridHeight):
            for column in range(gridWidth):
                color = GameConstants.ColorLightGray
                colorCircle = GameConstants.ColorBackground

                if self.bitPosition(0, row, column) == "1":
                    colorCircle = GameConstants.ColorRed
                elif self.bitPosition(1, row, column) == "1":
                    colorCircle = GameConstants.ColorYellow

                cellMargin = GameConstants.gridMarginSize
                cellWidth = GameConstants.gridCellWidth
                cellHeight = GameConstants.gridCellHeight

                rect = pygame.draw.rect(
                    screen,
                    color,
                    [
                        cellWidth * column + cellMargin,
                        cellHeight * row + cellMargin,
                        cellWidth - 2 * cellMargin,
                        cellHeight - 2 * cellMargin,
                    ],
                )

                rects += [rect]

                radius = ((cellWidth / 2) * 80) / 100

                circle = pygame.draw.circle(
                    screen,
                    colorCircle,
                    (
                        (cellWidth / 2) + (cellWidth * column),
                        (cellHeight / 2) + (cellHeight * row),
                    ),
                    radius,
                )

                rects += [circle]

        return rects