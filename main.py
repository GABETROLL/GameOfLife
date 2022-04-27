import pygame

WIDTH = 800

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


def display(window, board: set, width: int, rows: int):
    window.fill(BLACK)

    block_width = width // rows

    for (x_pos, y_pos) in board:
        pygame.draw.rect(window, WHITE, pygame.Rect(block_width * x_pos, block_width * y_pos, block_width, block_width))


def draw(board: set, width: int, rows: int, erasing=False):
    mouse_pos = pygame.mouse.get_pos()

    block_width = width // rows
    board_pos = (mouse_pos[0] // block_width, mouse_pos[1] // block_width)

    if erasing:
        if board_pos in board:
            board.remove(board_pos)
    else:
        board.add(board_pos)


def main(rows: int):
    window = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption("Game Of Life")
    clock = pygame.time.Clock()
    running = True

    board = set()

    drawing = True

    previous_space = False

    while running:
        clock.tick(20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if drawing:
            mouse_buttons = pygame.mouse.get_pressed(3)
            if mouse_buttons[0]:
                draw(board, WIDTH, rows)
            elif mouse_buttons[2]:
                draw(board, WIDTH, rows, erasing=True)
        else:
            board = play(board, rows)

        current_space = keys[pygame.K_SPACE]
        if current_space and not previous_space:
            drawing = not drawing

        previous_space = current_space
        # press space bar once.

        display(window, board, WIDTH, rows)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main(100)
