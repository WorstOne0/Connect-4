import pygame
import numpy as np
from scipy.signal import convolve2d

from __init__ import GameConstants


class Board:
    grid = []

    rows = 0
    columns = 0

    playedMoves = 0

    def __init__(self, rows, columns):
        self.grid = np.full((rows, columns), None)

        self.rows = rows
        self.columns = columns

    def addChip(self, player, column):
        gravity = self.rows - 1

        while gravity > 0:
            if self.grid[gravity][column] == None:
                break

            gravity -= 1

        if self.grid[gravity][column] == None:
            self.grid[gravity][column] = player
            self.playedMoves += 1

    def removeChip(self, player, column):
        gravity = 0

        while gravity < self.rows - 1:
            if self.grid[gravity][column] == player:
                break

            gravity += 1

        if self.grid[gravity][column] == player:
            self.grid[gravity][column] = None
            self.playedMoves -= 1

    def isColumnMoveAllowed(self, column):
        for row in range(self.rows):
            if self.grid[row][column] == None:
                return True

        return False

    def checkObjective(self, player):
        # Check if the player win
        # https://stackoverflow.com/questions/29949169/python-connect-4-check-win-function

        horizontal_kernel = np.array([[1, 1, 1, 1]])
        vertical_kernel = np.transpose(horizontal_kernel)
        diag1_kernel = np.eye(4, dtype=np.uint8)
        diag2_kernel = np.fliplr(diag1_kernel)
        detection_kernels = [
            horizontal_kernel,
            vertical_kernel,
            diag1_kernel,
            diag2_kernel,
        ]

        for kernel in detection_kernels:
            if (convolve2d(self.grid == player, kernel, mode="valid") == 4).any():
                return True

        return False

    def isMovesLeft(self):
        return False if self.playedMoves == self.rows * self.columns else True

    def draw(self, screen, game):
        rects = []

        rects = [screen.fill(GameConstants.ColorBackground)]

        gridWidth = self.columns
        gridHeight = self.rows

        for row in range(gridHeight):
            for column in range(gridWidth):
                color = GameConstants.ColorLightGray
                colorCircle = GameConstants.ColorBackground

                if self.grid[row][column] == 0:
                    colorCircle = GameConstants.ColorRed
                elif self.grid[row][column] == 1:
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