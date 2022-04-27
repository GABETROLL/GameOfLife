def custom_number_base(length: int, items: list):
    for i in items:
        if length == 1:
            yield [i]
        else:
            for new in custom_number_base(length - 1, items):
                yield [i] + new


def neighbors(board: set, pos: tuple[int, int]):
    result = {True: [], False: []}

    for move in custom_number_base(2, [-1, 0, 1]):
        if move == [0, 0]:
            continue

        neighbor = (pos[0] + move[0], pos[1] + move[1])
        result[neighbor in board].append(neighbor)

    return result


def play(board: set, rows: int):
    new_board = set()

    for cell in board:
        # Look only at the live cells.
        cell_neighbors = neighbors(board, cell)
        neighbor_count = len(cell_neighbors[True])

        if neighbor_count == 2 or neighbor_count == 3:
            new_board.add(cell)
        # Apply the rules to the live cells.

        for empty_neighbor in cell_neighbors[False]:
            # Look at the live cell's dead neighbor cells.
            empty_cell_neighbors = neighbors(board, empty_neighbor)

            if len(empty_cell_neighbors[True]) == 3:
                new_board.add(empty_neighbor)
            # Apply the rules to the live cell's dead neighbor cells.
    # Since dead cells becoming alive takes more than one neighbor,
    # dead cells with no alive neighbor cells don't need to be considered.
    return new_board
