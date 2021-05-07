import pygame
import sys
import os
import random
import math
import numpy as np
from time import time

from __init__ import GameConstants

from bit_board import Board
from transposition import TranspositionTable

# from board import Board

COLUMN_ORDER = [3, 4, 2, 5, 1, 6, 0]


class Game:
    currentPlayer = 0
    moves = []

    board = Board(GameConstants.gridHeight, GameConstants.gridWidth)
    table = [TranspositionTable({}), TranspositionTable({})]

    nodeCount = 0
    move = 0

    def __init__(self):
        self.alive = True

        # self.currentPlayer = self.board.insertPosition("3333335444541442")

        # Bot as player one
        # Make the first optimal move
        # self.board.addChip(0, 3)
        # self.currentPlayer = 1

    def terminalNode(self, board):
        if (
            board.checkObjective(0)
            or board.checkObjective(1)
            or board.isMovesLeft() == False
        ):
            return True

        return False

    def scoreEvaluationMiniMax(self, board):
        # Red Wins
        if board.checkObjective(0):
            return (self.board.rows * self.board.columns) - self.board.playedMoves

        # Yellow Wins
        if board.checkObjective(1):
            return -(self.board.rows * self.board.columns) - self.board.playedMoves

        return 0

    def minimax(self, board, depth, alpha, beta, isMax):
        self.nodeCount += 1

        # Draw or there is no moves left
        if depth == 0 or self.terminalNode(board) == True:
            return self.scoreEvaluationMiniMax(board)

        # Red Move
        if isMax:
            best = -math.inf

            # Checking the center columns first
            for column in COLUMN_ORDER:
                if board.isColumnMoveAllowed(column):
                    board.addChip(0, column)

                    move = self.minimax(board, depth - 1, alpha, beta, False)
                    best = max(best, move)

                    board.removeChip(0, column)

                    alpha = max(alpha, move)
                    if beta <= alpha:
                        break

            return best

        # Yellow Move
        else:
            best = math.inf

            # Checking the center columns first
            for column in COLUMN_ORDER:
                if board.isColumnMoveAllowed(column):
                    board.addChip(1, column)

                    move = self.minimax(board, depth - 1, alpha, beta, True)
                    best = min(best, move)

                    board.removeChip(1, column)

                    beta = min(beta, move)
                    if beta <= alpha:
                        break

            return best

    def scoreEvaluationNegaMax(self, board, player):
        if board.checkObjective(player):
            return -((self.board.rows * self.board.columns) - self.board.playedMoves)

        return 0

    def negaMax(self, board, depth, alpha, beta, player):
        self.nodeCount += 1

        opponent = 1 if player == 0 else 0
        flag = 1

        tableEntry = self.table[opponent].getEntry(board.bitBoard[opponent])

        if tableEntry != None and tableEntry["depth"] >= depth:
            if tableEntry["flag"] == 0:
                return tableEntry["score"]

            if (tableEntry["flag"] == 1) and (tableEntry["score"] <= alpha):
                return alpha

            if (tableEntry["flag"] == -1) and (tableEntry["score"] >= beta):
                return beta

        # Draw or there is no moves left
        if depth == 0 or self.terminalNode(board) == True:
            score = self.scoreEvaluationNegaMax(board, opponent)

            self.table[opponent].addEntry(board.bitBoard[opponent], score, depth, 0)

            return score

        # Checking the center columns first
        for column in COLUMN_ORDER:
            if board.isColumnMoveAllowed(column):
                board.addChip(player, column)

                move = -self.negaMax(board, depth - 1, -beta, -alpha, opponent)

                board.removeChip(player, column)

                if move >= beta:
                    self.table[opponent].addEntry(
                        board.bitBoard[opponent], beta, depth, -1
                    )
                    return beta

                if move > alpha:
                    flag = 0
                    alpha = move

        self.table[opponent].addEntry(board.bitBoard[opponent], alpha, depth, flag)
        return alpha

    def laplaceFunction(self):
        player = 1 if self.currentPlayer == 0 else 0
        opponent = self.currentPlayer

        bestValue = math.inf if player == 1 else -math.inf
        bestMove = -1

        startTime = time()
        # The row does not matter, because the chip will fall
        # Checking the center columns first
        for column in COLUMN_ORDER:
            # If on that column is a space left
            if self.board.isColumnMoveAllowed(column):
                # Make the move
                self.board.addChip(player, column)

                moveValue = self.negaMax(self.board, 17, -math.inf, math.inf, opponent)

                # moveValue = self.minimax(
                #     self.board, 3, -math.inf, math.inf, True if player == 1 else False
                # )
                print("Col {}, move [{}]".format(column, moveValue))

                self.board.removeChip(player, column)

                if player == 1:
                    if moveValue < bestValue:
                        bestMove = column
                        bestValue = moveValue
                else:
                    if moveValue > bestValue:
                        bestMove = column
                        bestValue = moveValue
        endTime = time()

        print(endTime - startTime)

        return bestMove

    def update(self):
        if not self.moves or not self.alive:
            return

        row, column = self.moves.pop()

        if not self.board.isColumnMoveAllowed(column):
            return

        # Add move
        self.board.addChip(self.currentPlayer, column)

        if self.board.checkObjective(self.currentPlayer):
            self.alive = False
            print(
                "Player {} win's".format("Red" if self.currentPlayer == 0 else "Yellow")
            )
            return

        # Bot moves
        opponent = 1 if self.currentPlayer == 0 else 0

        bestMove = self.laplaceFunction()
        print("Best move [{}]".format(bestMove))
        print(self.nodeCount)

        self.nodeCount = 0

        self.board.addChip(opponent, bestMove)
        self.currentPlayer = opponent

        if self.board.checkObjective(self.currentPlayer):
            self.alive = False
            print("Player Yellow win's")
            return

        # Change player
        if self.currentPlayer == 0:
            self.currentPlayer = 1
        elif self.currentPlayer == 1:
            self.currentPlayer = 0


def initialize():
    pygame.init()

    game = Game()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode(
        (GameConstants.screenWidth, GameConstants.screenHeight)
    )

    return screen, game, clock


def main():
    screen, game, clock = initialize()

    running = True

    while running:
        # Handle user actions
        handleEvents(game)

        # Update
        game.update()

        # Draw
        rects = game.board.draw(screen, game)
        pygame.display.update(rects)

        # FPS
        clock.tick(GameConstants.FPS)


def handleEvents(game):
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()

            column = pos[0] // (GameConstants.screenWidth // GameConstants.gridWidth)
            row = pos[1] // (GameConstants.screenHeight // GameConstants.gridHeight)

            game.moves.append((row, column))

        # Esc key or press Close to quit
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)

    main()