import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def custom_number_base(length: int, items: list):
    for i in items:
        if length == 1:
            yield [i]
        else:
            for new in custom_number_base(length - 1, items):
                yield [i] + new


def neighbor_count(board: set, pos: tuple[int, int]):
    count = 0

    for move in custom_number_base(2, [-1, 0, 1]):
        if move == [0, 0]:
            continue

        if (pos[0] + move[0], pos[1] + move[1]) in board:
            count += 1

    return count


def play(board: set, rows: int):
    new_board = set()

    for i in range(rows):
        for j in range(rows):
            count = neighbor_count(board, (i, j))

            if count == 3 or ((i, j) in board and count == 2):
                new_board.add((i, j))

    return new_board
