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

    # Bit Board
    board = Board(GameConstants.gridHeight, GameConstants.gridWidth)
    # Separate Transposition Table
    table = [TranspositionTable({}), TranspositionTable({})]

    nodeCount = 0

    def __init__(self):
        self.alive = True

        # Bot as player one
        # Make the first optimal move
        # self.board.addChip(0, 3)
        # self.currentPlayer = 1

    # Return if is a terminal node
    def terminalNode(self, board):
        if (
            board.checkObjective(0)
            or board.checkObjective(1)
            or board.isMovesLeft() == False
        ):
            return True

        return False

    # Evaluation function for MiniMax
    def scoreEvaluationMiniMax(self, board):
        # Red Wins
        if board.checkObjective(0):
            return (self.board.rows * self.board.columns) - self.board.playedMoves

        # Yellow Wins
        if board.checkObjective(1):
            return -(self.board.rows * self.board.columns) - self.board.playedMoves

        return 0

    # MiniMax algorithm
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

    # The score we are using is the number of winning spots the current player has after playing the move.
    def moveScore(self, board):
        pass

    # Evaluation function for NegaMax
    def scoreEvaluationNegaMax(self, board, player):
        if board.checkObjective(player):
            return -((self.board.rows * self.board.columns) - self.board.playedMoves)

        # Draw
        return 0

    # NegaMax algorithm
    def negaMax(self, board, depth, alpha, beta, player):
        self.nodeCount += 1

        # Change turn's
        opponent = 1 if player == 0 else 0

        # Defines if the score will be an Upper Bound, Lower Bound or an Exact Value
        flag = 1  # Starts with Upper Bound

        # Lookup to the Table to see if finds this positon on the board
        tableEntry = self.table[opponent].getEntry(board.bitBoard[opponent])

        # If finds an entry and we have searched the tree NOT shallower before, then
        if tableEntry != None and tableEntry["depth"] >= depth:
            if tableEntry["flag"] == 0:
                return tableEntry["score"]

            if (tableEntry["flag"] == 1) and (tableEntry["score"] <= alpha):
                return alpha

            if (tableEntry["flag"] == -1) and (tableEntry["score"] >= beta):
                return beta

        if depth == 0 or self.terminalNode(board) == True:
            # Get the evaluation of the board - Win / Loss / Draw
            score = self.scoreEvaluationNegaMax(board, opponent)

            # Add's to the table with a flag Exact
            self.table[opponent].addEntry(board.bitBoard[opponent], score, depth, 0)

            return score

        # Checking the center columns first
        for column in COLUMN_ORDER:
            # If the column is avaliable
            if board.isColumnMoveAllowed(column):
                # Make the move
                board.addChip(player, column)

                # Call NegaMax for the opponent
                move = -self.negaMax(board, depth - 1, -beta, -alpha, opponent)

                # Undo the move
                board.removeChip(player, column)

                # Beta cut-off
                if move >= beta:
                    # Add's to the table with a flag Lower Bound
                    self.table[opponent].addEntry(
                        board.bitBoard[opponent], beta, depth, -1
                    )

                    return beta

                # If the move is better than alpha(best move) - alpha = max(alpha, move)
                if move > alpha:
                    flag = 0  # Change the flag to Exact move
                    alpha = move  # Setthe new best move

        # At the end, add the best move to the table
        self.table[opponent].addEntry(board.bitBoard[opponent], alpha, depth, flag)

        # Return best move
        return alpha

    # Find the best move
    def laplaceFunction(self):
        player = 1 if self.currentPlayer == 0 else 0
        opponent = self.currentPlayer

        # Start with the worst value for the player
        bestValue = math.inf if player == 1 else -math.inf
        # Worst move
        bestMove = -1

        startTime = time()
        # The row does not matter, because the chip will fall

        # Checking the center columns first
        for column in COLUMN_ORDER:
            # If the column is avaliable
            if self.board.isColumnMoveAllowed(column):
                # Make the move
                self.board.addChip(player, column)

                # Call NegaMax for the opponent
                moveValue = self.negaMax(self.board, 17, -math.inf, math.inf, opponent)

                # moveValue = self.minimax(self.board, 7, -math.inf, math.inf, True if player == 1 else False)
                print("Col {}, move [{}]".format(column, moveValue))

                # Undo the move
                self.board.removeChip(player, column)

                if player == 1:
                    # The maximizing player wants the highest value
                    if moveValue < bestValue:
                        bestMove = column
                        bestValue = moveValue
                else:
                    # The minimizing player wants the lowest value
                    if moveValue > bestValue:
                        bestMove = column
                        bestValue = moveValue
        endTime = time()

        print(endTime - startTime)

        return bestMove

    def update(self):
        # If nothing change just return
        if not self.moves or not self.alive:
            return

        # Get the position where the player clicked
        row, column = self.moves.pop()

        # If the column is not avaliable just return
        if not self.board.isColumnMoveAllowed(column):
            return

        # Make the move
        self.board.addChip(self.currentPlayer, column)

        # Sees if current player win's
        if self.board.checkObjective(self.currentPlayer):
            # Game Over
            self.alive = False

            print(
                "Player {} win's".format("Red" if self.currentPlayer == 0 else "Yellow")
            )

            return

        ## Bot moves
        opponent = 1 if self.currentPlayer == 0 else 0

        # Find the best move
        bestMove = self.laplaceFunction()
        print("Best move [{}]".format(bestMove))
        print(self.nodeCount)

        self.nodeCount = 0

        # Make the bot move
        self.board.addChip(opponent, bestMove)
        # Change turn
        self.currentPlayer = opponent

        # Sees if current player win's
        if self.board.checkObjective(self.currentPlayer):
            # Game Over
            self.alive = False

            print(
                "Player {} win's".format("Red" if self.currentPlayer == 0 else "Yellow")
            )

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